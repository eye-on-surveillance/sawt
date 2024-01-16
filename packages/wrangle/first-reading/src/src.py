from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import JSONLoader
import json
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re
from pdfminer.high_level import extract_text


def save_ocr_to_json(
    pdf_path, ocr_json_path, publish_date, text_output_path="test.txt"
):
    """Extracts text from the last 10 pages of a PDF and saves the result in a JSON format with page numbers, and also saves these pages as a text file."""
    full_text = extract_text_from_pdf(pdf_path)

    pages = full_text.split("\f")[:-1]

    last_10_pages = pages[-10:] if len(pages) >= 10 else pages

    messages = []
    combined_text = ""
    for page_num, page_text in enumerate(
        last_10_pages, start=len(pages) - len(last_10_pages) + 1
    ):
        record = {"page_content": page_text, "metadata": {"page_number": page_num}}
        messages.append(record)
        combined_text += page_text + "\n\n"

    with open(ocr_json_path, "w") as file:
        json.dump({"messages": messages, "publish_date": publish_date}, file, indent=4)

    with open(text_output_path, "w", encoding="utf-8") as text_file:
        text_file.write(combined_text)


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file"""
    return extract_text(pdf_path)


def load_and_split(json_path, chunk_size=2000, chunk_overlap=1000):
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
    texts = text_splitter.split_documents(data)
    return texts


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

    combined_text_content = " ".join(chunk.page_content for chunk in chunks[:10])

    ord_num_prompt = PromptTemplate(
        input_variables=["text_content"],
        template="""
        ### System Instructions:
        - Find this section: 'ORDINANCES ON FIRST READING'. Immediately preceding this heading will be a two-digit number, followed by a period (e.g., '35.', '40.', '50.', etc.). 
        - Your primary task is to identify and extract the two-digit ordinance number, which precedes the 'ORDINANCES ON FIRST READING' heading.
        
        Ordinances on First Reading Identifier: 

        ### Documents for the system to inspect:
        {text_content}
    """,
    )

    ord_num_chain = LLMChain(llm=chat, prompt=ord_num_prompt)
    ord_num = ord_num_chain.run(text_content=combined_text_content, temperature=1)
    print(ord_num)

    summaries = []
    for chunk in chunks:
        text_content = chunk.page_content

        prompt = PromptTemplate(
            input_variables=["text_content", "ord_num"],
            template="""
            System Instructions:

            Analyze the document text provided to locate ordinances specifically from the 'ORDINANCES ON FIRST READING' section, which begins with the number found here '{ord_num}'. Disregard the string of text before the number. Focus on ordinances prefixed with '{ord_num}' followed by a letter (e.g., '{ord_num}a', '{ord_num}b', '{ord_num}c', etc.).

            For each identified ordinance, extract and compile the following details:

            - The ordinance prefix (e.g., '{ord_num}a').
            - The full ordinance number and identifier, such as '51a. CAL. NO. 34,462 BY COUNCILMEMBER HARRIS'.
            - A comprehensive summary of the ordinance's content and purpose.
            - The names of council members who introduced the ordinance.
            - The general topic or keywords of the ordinance (limit to 3 topics).
            - The original ordinance on first reading number from here {ord_num}

            Format each ordinance's information as a JSON object, including the keys: "Full Ordinance Number", "First Reading Ordinance Number", "Summary", "Introduced By", "Topic/Tag/Keywords", "Original Ordinance on First Reading Number".

            Begin the analysis with the following document text:
            {text_content}
        """,
        )

        chain = LLMChain(llm=chat, prompt=prompt)
        summary = chain.run(text_content=text_content, ord_num=ord_num, temperature=1)
        print(summary)
        summaries.append(
            {"page_content": summary, "publish_date": publish_date, "title": title}
        )

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
        json_regex = r"\{\n\s+\"Full Ordinance Number\":.*?\n\}"

        json_matches = re.findall(json_regex, page_content, re.DOTALL)

        for json_match in json_matches:
            try:
                ordinance_dict = json.loads(json_match)
                ordinance_dict["publish_date"] = message["publish_date"]
                ordinance_dicts.append(ordinance_dict)
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {json_match}")

    return ordinance_dicts


def deduplicate_ordinances(ordinances):
    """
    Deduplicates the list of ordinances based on the full ordinance number.
    Keeps the ordinance with the longest summary if duplicates are found.
    """
    deduped_ordinances = {}
    for ordinance in ordinances:
        full_ordinance_number = ordinance.get("Full Ordinance Number", "")

        existing_ordinance = deduped_ordinances.get(full_ordinance_number)
        if existing_ordinance:
            if len(ordinance.get("Summary", "")) > len(
                existing_ordinance.get("Summary", "")
            ):
                deduped_ordinances[full_ordinance_number] = ordinance
        else:
            deduped_ordinances[full_ordinance_number] = ordinance

    return list(deduped_ordinances.values())


if __name__ == "__main__":
    documents_directory = "../data/input"
    output_json_dir = "../data/output"

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
            ocr_json_path = "../data/output/ocr_text.json"

            save_ocr_to_json(pdf_path, ocr_json_path, publish_date)
            chunks = load_and_split(ocr_json_path)
            summaries = summarize_text(chunks, publish_date, title)
            individual_ordinances = split_ordinance_summaries(summaries)
            deduplicated_ordinances = deduplicate_ordinances(individual_ordinances)

            save_summaries_to_json(
                deduplicated_ordinances, output_json_dir, pdf_filename
            )
            os.remove(ocr_json_path)

    input_directory = "../data/output"
    output_json_path = "../data/output/First Reading.json"
    concatenate_jsons(input_directory, output_json_path)
    print(f"Summaries saved in directory: {output_json_dir}")
