import logging

from input_video_urls import CJ_INPUT_VIDEO_URLS, FC_INPUT_VIDEO_URLS
from dotenv import find_dotenv, load_dotenv
from preprocessor import create_db_from_youtube_urls_and_pdfs, create_embeddings, create_db_from_fc_youtube_urls

load_dotenv(find_dotenv())

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    pdf_directory = "agendas_minutes_pdfs"
    print(f"Preprocessing videos, agendas, and minutes to generate a cache.")
    general_embeddings, in_depth_embeddings = create_embeddings()

    # create_db_from_fc_youtube_urls(FC_INPUT_VIDEO_URLS)
    create_db_from_youtube_urls_and_pdfs(
        FC_INPUT_VIDEO_URLS,
        CJ_INPUT_VIDEO_URLS,
        pdf_directory,
        general_embeddings,
        in_depth_embeddings,
    )


if __name__ == "__main__":
    main()
