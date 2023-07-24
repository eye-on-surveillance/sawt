from ocr import process_pdfs

doc_input_directory = "../../backend/src/minutes_agendas_directory/pdfs"
text_output_directory = "output/txt"
docx_output_directory = "../../backend/src/minutes_agendas_directory"
csv_output_directory = "output/ocr_results.xlsx"

if __name__ == "__main__":
    process_pdfs(doc_input_directory, text_output_directory, docx_output_directory, csv_output_directory)