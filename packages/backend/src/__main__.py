import logging

from input_video_urls import INPUT_VIDEO_URLS
from dotenv import find_dotenv, load_dotenv
from preprocessor import create_db_from_youtube_urls

load_dotenv(find_dotenv())

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

def main():
    print(f"Preprocessing {len(INPUT_VIDEO_URLS)} videos and generating a cache.")
    create_db_from_youtube_urls(INPUT_VIDEO_URLS)

if __name__ == "__main__":
    main()