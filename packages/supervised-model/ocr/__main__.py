from ocr import process_pdfs

doc_directory = "../../backend/src/minutes_agendas_directory/pdfs"
text_directory = "output/agendas_minutes_texts"
docx_directory = "../../backend/src/minutes_agendas_directory"
csv_directory = "output/ocr_results.xlsx"

if __name__ == "__main__":
    process_pdfs(doc_directory, text_directory, docx_directory, csv_directory)