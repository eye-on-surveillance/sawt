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

def getcreds():
    with open("creds.txt", "r") as c:
        creds = c.readlines()
    return creds[0].strip(), creds[1].strip()


def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

class DocClient:
    def __init__(self, endpoint, key, text_directory, docx_directory):
        self.client = ComputerVisionClient(
            endpoint, CognitiveServicesCredentials(key)
        )
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

    def pdf2txt(self, pdf_path):
        with open(pdf_path, "rb") as file:
            pdf_data = file.read()
            num_pages = pdf2image.pdfinfo_from_bytes(pdf_data)['Pages']

            all_text = []

            for i in range(num_pages):
                try:
                    image = pdf2image.convert_from_bytes(pdf_data, dpi=300, first_page=i+1, last_page=i+1)[0]

                    img_byte_arr = BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)

                    ocr_result = self.client.read_in_stream(img_byte_arr, raw=True)

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

        outname = os.path.basename(pdf_path).replace(".pdf", "")
        outstring_txt = os.path.join(self.text_directory, "{}.txt".format(outname))
        outpath_txt = os.path.abspath(outstring_txt)
        outstring_docx = os.path.join(self.docx_directory, "{}.docx".format(outname))
        outpath_docx = os.path.abspath(outstring_docx)

        if os.path.exists(outpath_txt) and os.path.exists(outpath_docx):
            logging.info(f"skipping {outpath_txt} and {outpath_docx}, files already exist")
            return None

        logging.info(f"sending document {outname}")
        logging.info(f"writing to {outpath_txt} and {outpath_docx}")

        with open(outpath_txt, 'w') as f:
            f.write(full_text)

        doc = Document()
        doc.add_paragraph(full_text)
        doc.save(outpath_docx)

        return outpath_txt

def process_pdfs(doc_directory, text_directory, docx_directory, csv_directory):
    logger = logging.getLogger()
    azurelogger = logging.getLogger("azure")
    logger.setLevel(logging.INFO)
    azurelogger.setLevel(logging.ERROR)

    if not os.path.exists(text_directory):
        os.makedirs(text_directory)

    endpoint, key = getcreds()
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
                chunks = chunkstring(text, 32000)  # Limiting chunks to 32000 characters
                for i, chunk in enumerate(chunks):
                    df.loc[len(df)] = [text_file_path, i+1, f'"""{chunk}"""']

    df.to_excel(csv_directory, index=False)

    client.close()
