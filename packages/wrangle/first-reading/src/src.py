import pytesseract
from pdf2image import convert_from_path
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import JSONLoader
import json
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import uuid
import re
import PyPDF2


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
        api_key="",
    )
    summaries = []
    for chunk in chunks:
        text_content = chunk.page_content
        metadata = chunk.metadata

        prompt = PromptTemplate(
            input_variables=["text_content"],
            template="""
        ## Council Meeting Ordinance Summary on First Reading

        ### Text Content:
        {text_content}

        ### Instructions:
        - Begin by identifying the section titled 'ORDINANCES ON FIRST READING'. This section will start with a number (e.g., '35. ORDINANCES ON FIRST READING').
        - Once the starting point is found, extract all subsequent ordinances. These will be marked with the same prefix number followed by a letter (e.g., '35a.', '35b.', etc.).
        - For each ordinance, create a JSON object with keys for the ordinance number, a summary of the ordinance, the names of council members who introduced it, and relevant topics/tags/keywords.
        - Stop extracting once a different section heading is encountered.

        ### Example Format:
        Create a JSON object for each ordinance summary:
            "Ordinance Number": "35a.",
            "Summary": "A brief summary of the ordinance's content and purpose.",
            "Introduced By": "Names of council members who introduced the ordinance"
            "Topic/Tag/Keywords": "The general topic of the ordinance (e.g., budget, criminal justice, environmental, housing, etc.)",


        ### Role Emphasis:
        As an AI assistant, your task is to meticulously identify ordinances on first reading by their unique prefix syntax and provide clear, concise, and well-structured JSON summaries, enabling quick understanding and retrieval of essential details from the council meeting minutes.
        """,
        )

        chain = LLMChain(llm=chat, prompt=prompt)
        summary = chain.run(text_content=text_content, temperature=1)
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
                ordinance_dict["uid"] = message["uid"]
                ordinance_dict["publish_date"] = message["publish_date"]
                ordinance_dicts.append(ordinance_dict)
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {json_match}")

    return ordinance_dicts


if __name__ == "__main__":
    documents_directory = "../data"
    output_json_dir = "../output"

    os.makedirs(output_json_dir, exist_ok=True)  

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
            individual_ordinances = split_ordinance_summaries(summaries)

            save_summaries_to_json(individual_ordinances, output_json_dir, pdf_filename)

            os.remove(ocr_json_path)

    input_directory = "../output"
    output_json_path = "../output/First Reading.json"
    concatenate_jsons(input_directory, output_json_path)
    print(f"Summaries saved in directory: {output_json_dir}")
