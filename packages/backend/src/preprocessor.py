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

from langchain.document_loaders import PyPDFLoader, YoutubeLoader


def create_embeddings():
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

    return embeddings


def create_db_from_pdfs(pdf_directory):
    all_docs = []
    for pdf_file in os.listdir(pdf_directory):
        if not pdf_file.endswith(".pdf"):  # Skip non-pdf files
            continue
        pdf_path = os.path.join(pdf_directory, pdf_file)
        loader = PyPDFLoader(pdf_path)
        document = loader.load()
        if not document:  # Check if document is empty
            logger.error(f"No content found for PDF file: {pdf_path}")
            continue
        source_id = os.path.splitext(pdf_file)[
            0
        ]  # Using file name without extension as source_id
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=500
        )
        docs = text_splitter.split_documents(document)
        all_docs.extend(docs)
        logger.info(f"Finished processing {source_id}")
    return all_docs


def create_db_from_youtube_urls(video_urls):
    all_docs = []
    for video_info in video_urls:
        video_url = video_info["url"]
        logger.debug(f"Processing video URL: {video_url}")
        loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
        transcript = loader.load()
        if not transcript:  # Check if transcript is empty
            logger.error(f"No transcript found for video URL: {video_url}")
            continue
        source_id = transcript[0].metadata["title"]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=500
        )
        docs = text_splitter.split_documents(transcript)
        all_docs.extend(docs)
        logger.info(f"Finished processing {source_id}")
    return all_docs


def create_db_from_youtube_urls_and_pdfs(video_urls, pdf_directory, embeddings):
    video_docs = create_db_from_youtube_urls(video_urls)
    pdf_docs = create_db_from_pdfs(pdf_directory)

    all_docs = video_docs + pdf_docs
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

    logger.info(
        f"Combined database created from all video URLs and PDF files saved to {save_dir}"
    )
    return db
