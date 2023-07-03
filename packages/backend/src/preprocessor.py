import logging
import os
from langchain.document_loaders import (
    PyMuPDFLoader,
    JSONLoader,
    PyPDFLoader,
    PyPDFium2Loader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain, HypotheticalDocumentEmbedder
from langchain.prompts import PromptTemplate
from langchain.vectorstores.faiss import FAISS
from langchain.llms import OpenAI
from pathlib import Path
import shutil


logger = logging.getLogger(__name__)
dir = Path(__file__).parent.absolute()


def create_embeddings():
    llm = OpenAI()

    general_prompt_template = """
    As an AI assistant, your role is to generate brief, concise summaries from the transcripts of New Orleans City Council meetings in response to the question "{question}". Please ensure the response is balanced and succinct, not exceeding one paragraph in length. If the transcripts do not provide enough information to accurately summarize the issue, please respond with 'Insufficient information available'. If the question extends beyond the scope of information contained in the transcripts, respond with 'I don't know'.
    Answer:"""

    in_depth_prompt_template = """
    As an AI assistant, your role is to provide comprehensive, dialogical summaries from the transcripts of New Orleans City Council meetings in response to the question "{question}". Your response should mimic a real conversation, often involving multiple exchanges between city council members and external stakeholders. If the transcripts do not provide enough information to accurately answer the question or recreate the dialogue, respond with 'Insufficient information available'. If the question extends beyond the scope of the transcripts, respond with 'I don't know'.
    Answer:"""

    voting_template = """
    As an AI assistant tasked with providing comprehensive information from the transcripts of New Orleans City Council meetings, your role is to respond to the "{question}", which may be related to a vote or briefs on an ordinance that took place. Your response should include detailed information as available, which might cover:

    - The ordinance number or reference (often prefixed with 'CAL. NO.' or 'MOTION – NO.')
    - The details of the ordinance or motion
    - Who introduced the ordinance or motion
    - Relevant discussion points or concerns raised
    - Any action taken, including votes, if any (specifying the yeas, nays, abstentions, absences, and recusals)
    - The final outcome of the vote or the current status of the ordinance or motion, if it has not been voted upon yet

    Always refer back to the original transcript to ensure accuracy. If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    general_prompt = PromptTemplate(
        input_variables=["question"], template=general_prompt_template
    )
    in_depth_prompt = PromptTemplate(
        input_variables=["question"], template=in_depth_prompt_template
    )

    voting_prompt = PromptTemplate(
        input_variables=["question"], template=voting_template
    )

    llm_chain_general = LLMChain(llm=llm, prompt=general_prompt)
    llm_chain_in_depth = LLMChain(llm=llm, prompt=in_depth_prompt)
    llm_chain_voting = LLMChain(llm=llm, prompt=voting_prompt)

    base_embeddings = OpenAIEmbeddings()

    general_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_general, base_embeddings=base_embeddings
    )
    in_depth_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_in_depth, base_embeddings=base_embeddings
    )
    voting_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_voting, base_embeddings=base_embeddings
    )

    return general_embeddings, in_depth_embeddings, voting_embeddings


def create_db_from_minutes(doc_directory):
    all_docs = []
    for doc_file in os.listdir(doc_directory):
        if not doc_file.endswith(".pdf"):
            continue
        doc_path = os.path.join(doc_directory, doc_file)
        loader = PyMuPDFLoader(doc_path)
        document = loader.load()
        if not document:
            logger.error(f"No content found for PDF file: {doc_path}")
            continue
        source_id = os.path.splitext(doc_file)[0]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400, chunk_overlap=300
        )
        docs = text_splitter.split_documents(document)
        all_docs.extend(docs)
        logger.info(f"Finished processing {source_id}")
    return all_docs


def create_db_from_agendas(doc_directory):
    all_docs = []
    for doc_file in os.listdir(doc_directory):
        if not doc_file.endswith(".pdf"):
            continue
        doc_path = os.path.join(doc_directory, doc_file)
        loader = PyMuPDFLoader(doc_path)
        document = loader.load()
        if not document:
            logger.error(f"No content found for PDF file: {doc_path}")
            continue
        source_id = os.path.splitext(doc_file)[0]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400, chunk_overlap=300
        )
        docs = text_splitter.split_documents(document)
        all_docs.extend(docs)
        logger.info(f"Finished processing {source_id}")
    return all_docs


def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["timestamp"] = record.get("timestamp")
    metadata["url"] = record.get("url")
    metadata["title"] = record.get("title")
    metadata["publish_date"] = record.get("publish_date")

    return metadata


def create_db_from_cj_transcripts(cj_json_directory):
    logger.info("Creating database from CJ transcripts...")
    all_docs = []
    for doc_file in os.listdir(cj_json_directory):
        if not doc_file.endswith(".json"):
            continue
        doc_path = os.path.join(cj_json_directory, doc_file)
        loader = JSONLoader(
            file_path=doc_path,
            jq_schema=".messages[]",
            content_key="page_content",
            metadata_func=metadata_func,
        )

        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000, chunk_overlap=1500
        )
        docs = text_splitter.split_documents(data)
        all_docs.extend(docs)
    logger.info("Finished database from CJ transcripts...")
    return all_docs


def create_db_from_fc_transcripts(fc_json_directory):
    logger.info("Creating database from FC transcripts...")
    all_docs = []
    for doc_file in os.listdir(fc_json_directory):
        if not doc_file.endswith(".json"):
            continue
        doc_path = os.path.join(fc_json_directory, doc_file)
        loader = JSONLoader(
            file_path=doc_path,
            jq_schema=".messages[]",
            content_key="page_content",
            metadata_func=metadata_func,
        )

        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000, chunk_overlap=1500
        )
        docs = text_splitter.split_documents(data)
        all_docs.extend(docs)
    logger.info("Finished database from FC transcripts...")
    return all_docs


def create_db_from_youtube_urls_and_pdfs(
    fc_json_directory,
    cj_json_directory,
    minutes_directory,
    agendas_directory,
    general_embeddings,
    in_depth_embeddings,
    voting_embeddings,
):
    fc_video_docs = create_db_from_fc_transcripts(fc_json_directory)
    cj_video_docs = create_db_from_cj_transcripts(cj_json_directory)
    agendas = create_db_from_agendas(agendas_directory)
    minutes = create_db_from_minutes(minutes_directory)

    all_transcripts = fc_video_docs + cj_video_docs + agendas

    db_general = FAISS.from_documents(all_transcripts, general_embeddings)
    db_in_depth = FAISS.from_documents(all_transcripts, in_depth_embeddings)
    db_voting = FAISS.from_documents(minutes, voting_embeddings)

    cache_dir = dir.joinpath("cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    save_dir_general = cache_dir.joinpath("faiss_index_general")
    save_dir_in_depth = cache_dir.joinpath("faiss_index_in_depth")
    save_dir_voting = cache_dir.joinpath("faiss_index_voting")

    db_general.save_local(save_dir_general)
    db_in_depth.save_local(save_dir_in_depth)
    db_voting.save_local(save_dir_voting)

    # copy results to cloud function
    dest_dir_general = dir.parent.parent.joinpath(
        "googlecloud/functions/getanswer/cache/faiss_index_general"
    )
    dest_dir_in_depth = dir.parent.parent.joinpath(
        "googlecloud/functions/getanswer/cache/faiss_index_in_depth"
    )
    dest_dir_voting = dir.parent.parent.joinpath(
        "googlecloud/functions/getanswer/cache/faiss_index_voting"
    )

    shutil.copytree(save_dir_general, dest_dir_general, dirs_exist_ok=True)
    shutil.copytree(save_dir_in_depth, dest_dir_in_depth, dirs_exist_ok=True)
    shutil.copytree(save_dir_voting, dest_dir_voting, dirs_exist_ok=True)

    logger.info(
        f"Combined database for general model created from all video URLs and PDF files saved to {save_dir_general}"
    )
    logger.info(
        f"Combined database for in-depth model created from all video URLs and PDF files saved to {save_dir_in_depth}"
    )
    logger.info(
        f"Combined database for voting model created from all video URLs and PDF files saved to {save_dir_voting}"
    )
    return db_general, db_in_depth, db_voting
