import logging
import os
from langchain.document_loaders import YoutubeLoader, Docx2txtLoader
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


def create_embeddings():
    llm = OpenAI()

    prompt_template = """
    As an AI assistant, your role is to provide information from the transcripts of New Orleans City Council meetings. When responding to general queries, your response should mimic the structure of a real conversation, often involving more than two exchanges between the parties. In these cases, your dialogue should recreate the actual exchanges that occurred between city council members and external stakeholders (such as civil servants, law enforcement personnel, community members).
    
    For specific queries related to any votes that took place, your response should include detailed information. This should cover the ordinance number, who moved and seconded the motion, how each council member voted, and the final outcome of the vote. 
    
    In response to the question "{question}", for each statement, response, and voting action, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved.
    
    If a question is about the voting results on a particular initiative, include in your response how each council member voted, if they were present, and if there were any abstentions or recusals. Always refer back to the original transcript to ensure accuracy.

    If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    prompt = PromptTemplate(input_variables=["question"], template=prompt_template)

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    base_embeddings = OpenAIEmbeddings()

    embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain, base_embeddings=base_embeddings
    )

    return embeddings



def create_db_from_docx(doc_directory):
    all_docs = []
    for doc_file in os.listdir(doc_directory):
        if not doc_file.endswith(".docx"): 
            continue
        doc_path = os.path.join(doc_directory, doc_file)
        loader = Docx2txtLoader(doc_path)
        document = loader.load()
        if not document: 
            logger.error(f"No content found for Word Doc file: {doc_path}")
            continue
        source_id = os.path.splitext(doc_file)[
            0
        ]  
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2500, chunk_overlap=1250
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
            chunk_size=2000, chunk_overlap=1000
        )
        docs = text_splitter.split_documents(transcript)
        all_docs.extend(docs)
        logger.info(f"Finished processing {source_id}")
    return all_docs


def create_db_from_youtube_urls_and_pdfs(video_urls, doc_directory,  embeddings):
    video_docs = create_db_from_youtube_urls(video_urls)
    pdf_docs = create_db_from_docx(doc_directory)

    weighted_pdfs = pdf_docs * 2
    weighted_video_docs = video_docs * 3

    all_docs = weighted_video_docs + weighted_pdfs
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
