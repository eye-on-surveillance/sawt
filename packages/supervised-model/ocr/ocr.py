import os
import pandas as pd
import pdf2image  
import azure 
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO
import time
import logging
from docx import Document

def get_credentials(filename):
    try:
        with open(filename, "r") as c:
            creds = c.readlines()
        return creds[0].strip(), creds[1].strip()
    except FileNotFoundError:
        logging.error('Credentials file not found')
        return None, None
    except IndexError:
        logging.error('Credentials file is not correctly formatted')
        return None, None

def chunk_string(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def setup_logger():
    logger = logging.getLogger()
    azure_logger = logging.getLogger("azure")
    logger.setLevel(logging.INFO)
    azure_logger.setLevel(logging.ERROR)

class DocClient:
    def __init__(self, endpoint, key, text_directory, docx_directory):
        self.client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
        self.text_directory = text_directory
        self.docx_directory = docx_directory

    def close(self):
        self.client.close()

    def extract_content(self, result):
        contents = {
            "page": [],
            "content": [],
            "confidence": [],
        }

        for read_result in result.analyze_result.read_results:
            lines = read_result.lines
            lines.sort(key=lambda line: line.bounding_box[1])

            for line in lines:
                contents["page"].append(read_result.page)
                contents["content"].append(' '.join([word.text for word in line.words]))
                contents["confidence"].append(sum([word.confidence for word in line.words]) / len(line.words))

        return '\n'.join(contents["content"])  

    def convert_pdf_to_image(self, pdf_data, page):
        return pdf2image.convert_from_bytes(pdf_data, dpi=300, first_page=page+1, last_page=page+1)[0]

    def ocr_image(self, image):
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return self.client.read_in_stream(img_byte_arr, raw=True)

    def write_output_files(self, outpath_txt, outpath_docx, full_text):
        with open(outpath_txt, 'w') as f:
            f.write(full_text)

        doc = Document()
        doc.add_paragraph(full_text)
        doc.save(outpath_docx)

    def check_files_exist(self, outpath_txt, outpath_docx):
        return os.path.exists(outpath_txt) and os.path.exists(outpath_docx)

    def get_output_paths(self, pdf_path):
        outname = os.path.basename(pdf_path).replace(".pdf", "")
        outstring_txt = os.path.join(self.text_directory, "{}.txt".format(outname))
        outpath_txt = os.path.abspath(outstring_txt)
        outstring_docx = os.path.join(self.docx_directory, "{}.docx".format(outname))
        outpath_docx = os.path.abspath(outstring_docx)
        return outname, outpath_txt, outpath_docx

    def pdf2txt(self, pdf_path):
        with open(pdf_path, "rb") as file:
            pdf_data = file.read()
            num_pages = pdf2image.pdfinfo_from_bytes(pdf_data)['Pages']

            all_text = []

            for i in range(num_pages):
                try:
                    image = self.convert_pdf_to_image(pdf_data, i)
                    ocr_result = self.ocr_image(image)

                    operation_id = ocr_result.headers["Operation-Location"].split("/")[-1]

                    while True:
                        result = self.client.get_read_result(operation_id)
                        if result.status.lower() not in ['notstarted', 'running']:
                            break
                        time.sleep(1)

                    if result.status.lower() == 'failed':
                        logging.error(f"OCR failed for page {i+1} of file {pdf_path}")
                        continue

                    text = self.extract_content(result)
                    all_text.append(text)

                except azure.core.exceptions.HttpResponseError as e:
                    logging.error(f"Error processing page {i+1} of file {pdf_path}: {e}")
                    continue

        full_text = '\n\n'.join(all_text) 
        outname, outpath_txt, outpath_docx = self.get_output_paths(pdf_path)

        if self.check_files_exist(outpath_txt, outpath_docx):
            logging.info(f"skipping {outpath_txt} and {outpath_docx}, files already exist")
            return None

        logging.info(f"sending document {outname}")
        logging.info(f"writing to {outpath_txt} and {outpath_docx}")

        self.write_output_files(outpath_txt, outpath_docx, full_text)

        return outpath_txt

def process_pdfs(doc_directory, text_directory, docx_directory, csv_directory):
    setup_logger()

    if not os.path.exists(text_directory):
        os.makedirs(text_directory)

    endpoint, key = get_credentials("creds.txt")
    client = DocClient(endpoint, key, text_directory, docx_directory)

    files = [
        f
        for f in os.listdir(doc_directory)
        if os.path.isfile(os.path.join(doc_directory, f)) and f.endswith(".pdf")
    ]
    logging.info(f"starting to process {len(files)} files")

    df = pd.DataFrame(columns=["filename", "chunk", "text"])

    for file in files:
        text_file_path = client.pdf2txt(os.path.join(doc_directory, file))
        if text_file_path is not None:
            with open(text_file_path, 'r') as f:
                text = f.read()
                chunks = chunk_string(text, 32000)  
                for i, chunk in enumerate(chunks):
                    df.loc[len(df)] = [text_file_path, i+1, f'"""{chunk}"""']

    df.to_excel(csv_directory, index=False)

    client.close()
