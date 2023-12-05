import os
from summary_model import (
    pdf_to_images,
    extract_text_from_image,
    save_ocr_to_json,
    load_and_split,
    extract_date_from_filename,
    summarize_text,
    save_summaries_to_json,
    concatenate_jsons,
)


def main():
    documents_directory = "../../backend/src/minutes_agendas_directory/2021/pdfs"
    output_json_dir = "../../backend/src/minutes_agendas_directory/2021/json"

    os.makedirs(output_json_dir, exist_ok=True)

    for pdf_filename in os.listdir(documents_directory):
        if pdf_filename.endswith(".pdf"):
            output_json_path = os.path.join(
                output_json_dir, f"{os.path.splitext(pdf_filename)[0]}.json"
            )

            if os.path.exists(output_json_path):
                print(f"Skipping {pdf_filename}, output already exists.")
                continue

            pdf_path = os.path.join(documents_directory, pdf_filename)
            publish_date = extract_date_from_filename(pdf_filename)
            ocr_json_path = (
                "../../backend/src/minutes_agendas_directory/2022/json/ocr_text.json"
            )

            save_ocr_to_json(pdf_path, ocr_json_path, publish_date)
            chunks = load_and_split(ocr_json_path)
            summaries = summarize_text(chunks, publish_date)

            save_summaries_to_json(summaries, output_json_dir, pdf_filename)
            os.remove(ocr_json_path)

    input_json_directory = "../../backend/src/minutes_agendas_directory/2021/json"
    output_json_concat_path = (
        "../../backend/src/minutes_agendas_directory/Minutes 2021.json"
    )
    concatenate_jsons(input_json_directory, output_json_concat_path)
    print(f"Summaries saved in directory: {output_json_dir}")


if __name__ == "__main__":
    main()
