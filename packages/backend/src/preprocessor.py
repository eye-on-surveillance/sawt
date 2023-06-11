import logging
import os
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)
dir = Path(__file__).parent.absolute()

def create_db_from_youtube_urls(video_urls) -> FAISS:
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    all_docs = []
    for video_info in video_urls:
        video_url = video_info["url"]
        logger.info(f"Processing video URL: {video_url}")

        loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
        transcript = loader.load()
        logger.info(f"Transcript loaded for video URL: {video_url}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        docs = text_splitter.split_documents(transcript)
        print(docs)

        all_docs.extend(docs)

    db = FAISS.from_documents(all_docs, embeddings)

    cache_dir = dir.joinpath("cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    save_dir = cache_dir.joinpath("faiss_index")
    db.save_local(save_dir)

    # copy results to cloud function
    dest_dir = dir.parent.parent.joinpath("googlecloud/functions/getanswer/cache/faiss_index")
    shutil.copytree(save_dir, dest_dir, dirs_exist_ok=True)

    logger.info(f"Combined database created from all video URLs saved to {save_dir}")
    return db
