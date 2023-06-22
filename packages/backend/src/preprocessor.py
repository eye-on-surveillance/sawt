import logging
import os
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain, HypotheticalDocumentEmbedder
from langchain.prompts import PromptTemplate
from langchain.vectorstores.faiss import FAISS
from langchain.llms import OpenAI
from pathlib import Path
import shutil
import json
import datetime

logger = logging.getLogger(__name__)
dir = Path(__file__).parent.absolute()


def create_db_from_youtube_urls(video_urls) -> FAISS:
    llm = OpenAI()

    prompt_template = """
    As an AI assistant, your role is to recreate the actual dialogue that occurred between city council members and external stakeholders (such as civil servants, law enforcement personnel, community members) based on the transcripts from New Orleans City Council meetings. 
    In response to the question "{question}", your output should mimic the structure of a real conversation, which often involves more than two exchanges between the parties. 
    For each statement and response, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved.
    If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.
    Answer:"""
    prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    base_embeddings = OpenAIEmbeddings()

    embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain, base_embeddings=base_embeddings
    )

    all_docs = []
    all_metadata = {}
    for video_info in video_urls:
        video_url = video_info["url"]
        logger.debug(f"Processing video URL: {video_url}")

        loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
        transcript = loader.load()
        if not transcript:  # Check if transcript is empty
            logger.error(f"No transcript found for video URL: {video_url}")
            continue

        logger.debug(f"Transcript loaded for video URL: {video_url}")

        source_id = transcript[0].metadata["title"]

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=500
        )
        docs = text_splitter.split_documents(transcript)
        all_docs.extend(docs)
        logger.info(f"Finished processing {source_id}")

    db = FAISS.from_documents(all_docs, embeddings)

    cache_dir = dir.joinpath("cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    save_dir = cache_dir.joinpath("faiss_index")
    db.save_local(save_dir)

    # copy results to cloud function
    dest_dir = dir.parent.parent.joinpath(
        "googlecloud/functions/getanswer/cache/faiss_index"
    )
    shutil.copytree(save_dir, dest_dir, dirs_exist_ok=True)

    logger.info(f"Combined database created from all video URLs saved to {save_dir}")
    return db
