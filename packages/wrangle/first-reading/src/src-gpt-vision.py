import fitz
import base64
import pytesseract
import re
import json
import os

from PIL import Image, ImageEnhance
from pdf2image import convert_from_path

from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.document_loaders import JSONLoader
from langchain.schema.messages import HumanMessage


def pdf_to_images(pdf_path):
    """Converts PDF file to images"""
    return convert_from_path(pdf_path)


def extract_text_from_image(image):
    """Extracts text from an image object using OCR with enhanced DPI."""
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2)
    text = pytesseract.image_to_string(image)
    return text


def encode_page(page):
    """Encode a PDF page to base64"""
    pix = page.get_pixmap()
    img = pix.tobytes("png")
    return base64.b64encode(img).decode("utf-8")


def page_summarize(page_base64, prompt, ord_num):
    """Summarize a PDF page with specific focus on ord_num related ordinances"""
    chat = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=1024, api_key="")
    updated_prompt = prompt.format(ord_num=ord_num)  
    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": updated_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{page_base64}"},
                    },
                ]
            )
        ]
    )
    return msg.content


def generate_page_summaries(pdf_path, ord_num):
    """
    Generate summaries for the last 10 pages of a PDF.
    pdf_path: Path to the PDF file.
    """
    doc = fitz.open(pdf_path)
    num_pages = doc.page_count
    start_page = max(
        0, num_pages - 10
    )  

    prompt = """
        Ordinance first reading number: {ord_num}
        ### System Instructions:
        - Extract each ordinances from the 'ORDINANCES ON FIRST READING' section. Ordinances from this section begin with the number '{ord_num}' and are followed by a sequential letter (e.g., '{ord_num}a.', '{ord_num}b.', '{ord_num}c.', etc.).
        
        For example, if the ordinance first reading number is 51, an corresponding ordinance can be identified as "51a. CAL. NO. 34,462 - BY:COUNCILMEMBER HARRIS"

        ### Example Format: 
        For each ordinance, return the following pieces of data:
            "Full Ordinance Number": "ordinance number, letter, and the complete string of the ordinance number, including its identifier (for example: 50. CAL. NO. 34,461)",
            "First Reading Ordinance Number": "{ord_num}",
            "Summary": "The full summary of the ordinance's content and purpose.",
            "Introduced By": "Names of council members who introduced the ordinance",
            "Topic/Tag/Keywords": "General topic of the ordinance (e.g., budget, criminal justice, environmental, housing, etc.)". Do not list more than 3 topics,
        """
    output_data = []
    for i in range(start_page, num_pages):
        page = doc.load_page(i)
        base64_page = encode_page(page)
        summary = page_summarize(base64_page, prompt, ord_num)
        print(summary)
        output_data.append([i + 1, summary])  

    doc.close()
    return output_data


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


def extract_ord_num(chunks):
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
        - Carefully inspect the provided council meeting text to locate the 'ORDINANCES ON FIRST READING' section.
        - This section will always begin with a two-digit number, followed by a period (e.g., '35.', '40.', '50.', etc.). Immediately following this two-digit number, you will find the heading 'ORDINANCES ON FIRST READING'.
        - Your primary task is to identify and extract this initial two-digit ordinance number, which precedes the 'ORDINANCES ON FIRST READING' heading.
        
        The output should be formatted as a plain, unformatted numeric output. For example, if the number is 61, your response should be simply: 61.
        Ordinances on First Reading Identifier: 

        ### Documents for the system to inspect:
        {text_content}
    """,
    )

    ord_num_chain = LLMChain(llm=chat, prompt=ord_num_prompt)
    ord_num = ord_num_chain.run(text_content=combined_text_content, temperature=1)
    print(ord_num)
    return ord_num


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
            ord_num = extract_ord_num(chunks)
            output_data = generate_page_summaries(pdf_path, ord_num)

    input_directory = "../data/output"
    output_json_path = "../data/output/First Reading.json"
