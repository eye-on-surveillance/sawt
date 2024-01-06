import pytesseract
from pdf2image import convert_from_path
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import JSONLoader
import json
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re


def pdf_to_images(pdf_path):
    """Converts PDF file to images"""
    return convert_from_path(pdf_path)


def extract_text_from_image(image):
    """Extracts text from a single image using OCR"""
    return pytesseract.image_to_string(image)


def save_ocr_to_json(pdf_path, ocr_json_path, publish_date):
    """Performs OCR on the last 10 pages of a PDF and saves the result in a JSON format with page numbers"""
    images = pdf_to_images(pdf_path)
    messages = []

    start_page = max(0, len(images) - 10)
    for page_num, image in enumerate(images[start_page:], start=start_page):
        text = extract_text_from_image(image)
        record = {"page_content": text, "metadata": {"page_number": page_num + 1}}
        messages.append(record)

    with open(ocr_json_path, "w") as file:
        json.dump({"messages": messages, "publish_date": publish_date}, file, indent=4)


def load_and_split(json_path, chunk_size=4000, chunk_overlap=1000):
    """Loads OCR text from JSON and splits it into chunks that approximately span 2 pages"""
    loader = JSONLoader(
        file_path=json_path,
        jq_schema=".messages[]",
        content_key="page_content",
    )

    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(data)


def extract_date_from_filename(filename):
    """Extracts the publish date from the PDF filename using regex"""
    match = re.search(r"\d{1,2}-\d{1,2}-\d{4}", filename)
    return match.group(0) if match else None


def summarize_text(chunks, publish_date, title):
    """Summarizes the chunks of text"""
    chat = ChatOpenAI(
        model="gpt-3.5-turbo-1106",
        api_key="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",
    )

    combined_text_content = " ".join(chunk.page_content for chunk in chunks[:10])

    ord_num_prompt = PromptTemplate(
        input_variables=["text_content"],
        template="""
        ### System Instructions for Identifying Initial Ordinance Number:
        - Carefully inspect the provided council meeting text to locate the 'ORDINANCES ON FIRST READING' section.
        - This section will always begin with a two-digit number, followed by a period (e.g., '35.', '40.', '50.', etc.). Immediately following this two-digit number, you will find the heading 'ORDINANCES ON FIRST READING'.
        - Your primary task is to identify and extract this initial two-digit ordinance number, which precedes the 'ORDINANCES ON FIRST READING' heading.
        - Once identified, report this number clearly. It is essential for guiding the extraction of subsequent ordinances in the first readings section.
        - Do not consider any numbers that are not two digits as the initial ordinance number.

        ### Example of What to Look For:
        - If the section begins with an ordinance labeled '35.' and is immediately followed by the heading 'ORDINANCES ON FIRST READING', your response should be: "Initial Ordinance Number: 35."
        - Ignore any numbers that are not in the two-digit format or not immediately followed by the 'ORDINANCES ON FIRST READING' heading.

        ### Documents for the system to inspect:
        {text_content}
    """,
    )

    ord_num_chain = LLMChain(llm=chat, prompt=ord_num_prompt)
    ord_num = ord_num_chain.run(text_content=combined_text_content, temperature=1)

    summaries = []
    for chunk in chunks:
        text_content = chunk.page_content

        prompt = PromptTemplate(
            input_variables=["text_content", "ord_num"],
            template="""
        ### System Instructions:
        - The 'ORDINANCES ON FIRST READING' section in this document starts with ordinance number '{ord_num}'. Focus on extracting all subsequent ordinances that are marked with this number followed by a letter (e.g., if '{ord_num}' is extracted, then look for '{ord_num}a.', '{ord_num}b.', '{ord_num}c.', etc.).
        - For each ordinance that matches this pattern, create a JSON object with keys for the ordinance number, a summary, names of council members who introduced it, and relevant topics/tags/keywords.
        - Disregard any ordinances that do not follow the pattern of '{ord_num}' followed by a letter, as these are not part of the 'ORDINANCES ON FIRST READING' section.

        ### Example Format: 
        Create a JSON object for each ordinance summary:
            "Ordinance Number": "[{ord_num} + letter]",
            "Summary": "A brief summary of the ordinance's content and purpose.",
            "Introduced By": "Names of council members who introduced the ordinance",
            "Topic/Tag/Keywords": "General topic of the ordinance (e.g., budget, criminal justice, environmental, housing, etc.)",

        ### Role Emphasis:
        Focus on accurately identifying and summarizing the ordinances that follow the unique prefix syntax ('{ord_num}' + letter). Provide clear, concise, and well-structured JSON summaries for these ordinances only. Disregard non-first-reading ordinances.

        ### Documents for the system to inspect:
        {text_content}
        """,
        )

        chain = LLMChain(llm=chat, prompt=prompt)
        summary = chain.run(text_content=text_content, ord_num=ord_num, temperature=1)
        summaries.append(
            {"page_content": summary, "publish_date": publish_date, "title": title}
        )
        print(summaries)

    return summaries


def save_summaries_to_json(summaries, output_dir, pdf_filename):
    """Saves the summaries to a JSON file, with all summaries under the key 'messages'"""
    output_file = os.path.join(output_dir, f"{os.path.splitext(pdf_filename)[0]}.json")
    with open(output_file, "w") as file:
        json.dump({"messages": summaries}, file, indent=4)


def concatenate_jsons(input_dir, output_file):
    all_messages = []

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(input_dir, file_name)

            with open(file_path, "r") as file:
                data = json.load(file)
                messages = data.get("messages", [])

                all_messages.extend(messages)
    with open(output_file, "w") as file:
        json.dump({"messages": all_messages}, file, indent=4)


def split_ordinance_summaries(messages):
    """
    Splits ordinance summaries in 'messages' into individual dictionary objects.
    Each 'page_content' in 'messages' is expected to contain multiple JSON-like objects.
    """
    ordinance_dicts = []

    for message in messages:
        page_content = message["page_content"]
        json_regex = r"\{\n\s+\"Ordinance Number\":.*?\n\}"

        json_matches = re.findall(json_regex, page_content, re.DOTALL)

        for json_match in json_matches:
            try:
                ordinance_dict = json.loads(json_match)
                ordinance_dict["publish_date"] = message["publish_date"]
                ordinance_dicts.append(ordinance_dict)
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {json_match}")

    return ordinance_dicts


if __name__ == "__main__":
    documents_directory = "../data"
    output_json_dir = "../output"

    os.makedirs(output_json_dir, exist_ok=True)  #

    for pdf_filename in os.listdir(documents_directory):
        if pdf_filename.endswith(".pdf"):
            output_json_path = os.path.join(
                output_json_dir, f"{os.path.splitext(pdf_filename)[0]}.json"
            )
            title = os.path.splitext(pdf_filename)[0]

            if os.path.exists(output_json_path):
                print(f"Skipping {pdf_filename}, output already exists.")
                continue

            pdf_path = os.path.join(documents_directory, pdf_filename)
            publish_date = extract_date_from_filename(pdf_filename)
            ocr_json_path = "../output/ocr_text.json"

            save_ocr_to_json(pdf_path, ocr_json_path, publish_date)
            chunks = load_and_split(ocr_json_path)
            summaries = summarize_text(chunks, publish_date, title)
            print("Summaries before split_ordinance_summaries:", summaries)
            individual_ordinances = split_ordinance_summaries(summaries)

            save_summaries_to_json(individual_ordinances, output_json_dir, pdf_filename)
            os.remove(ocr_json_path)

    input_directory = "../output"
    output_json_path = "../output/First Reading.json"
    concatenate_jsons(input_directory, output_json_path)
    print(f"Summaries saved in directory: {output_json_dir}")
