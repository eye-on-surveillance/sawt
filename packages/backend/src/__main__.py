import logging

from input_video_urls import INPUT_VIDEO_URLS
from dotenv import find_dotenv, load_dotenv
from preprocessor import create_db_from_youtube_urls_and_pdfs, create_embeddings

load_dotenv(find_dotenv())

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    pdf_directory = "agenda_minutes_pdfs"
    print(f"Preprocessing videos, agendas, and minutes to generate a cache.")

    create_db_from_youtube_urls_and_pdfs(
        INPUT_VIDEO_URLS, pdf_directory, create_embeddings()
    )


if __name__ == "__main__":
    main()
