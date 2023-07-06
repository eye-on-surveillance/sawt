import logging
import os
from langchain.document_loaders import (
    Docx2txtLoader,
    JSONLoader,
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
    As an AI assistant tasked with generating brief general summaries, your role is to provide succinct, balanced information from the transcripts of New Orleans City Council meetings in response to the question "{question}". The response should not exceed one paragraph in length. If the available information from the transcripts is insufficient to accurately summarize the issue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    in_depth_prompt_template = """
    As an AI assistant tasked with providing in-depth dialogical summaries, your role is to provide comprehensive information from the transcripts of New Orleans City Council meetings. Your response should mimic the structure of a real conversation, often involving more than two exchanges between the parties. The dialogue should recreate the actual exchanges that occurred between city council members and external stakeholders in response to the question "{question}". For specific queries related to any votes that took place, your response should include detailed information. This should cover the ordinance number, who moved and seconded the motion, how each council member voted, and the final outcome of the vote. For each statement, response, and voting action, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved. If a question is about the voting results on a particular initiative, include in your response how each council member voted, if they were present, and if there were any abstentions or recusals. Always refer back to the original transcript to ensure accuracy. If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    general_prompt = PromptTemplate(
        input_variables=["question"], template=general_prompt_template
    )
    in_depth_prompt = PromptTemplate(
        input_variables=["question"], template=in_depth_prompt_template
    )

    llm_chain_general = LLMChain(llm=llm, prompt=general_prompt)
    llm_chain_in_depth = LLMChain(llm=llm, prompt=in_depth_prompt)

    base_embeddings = OpenAIEmbeddings()

    general_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_general, base_embeddings=base_embeddings
    )
    in_depth_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_in_depth, base_embeddings=base_embeddings
    )

    return general_embeddings, in_depth_embeddings


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
        source_id = os.path.splitext(doc_file)[0]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=500
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
            chunk_size=3500, chunk_overlap=1750
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
            chunk_size=3500, chunk_overlap=1750
        )
        docs = text_splitter.split_documents(data)
        all_docs.extend(docs)
    logger.info("Finished database from FC transcripts...")
    return all_docs


def create_db_from_youtube_urls_and_pdfs(
    fc_json_directory,
    cj_json_directory,
    doc_directory,
    general_embeddings,
    in_depth_embeddings,
):
    fc_video_docs = create_db_from_fc_transcripts(fc_json_directory)
    cj_video_docs = create_db_from_cj_transcripts(cj_json_directory)
    pdf_docs = create_db_from_docx(doc_directory)

    weighed_fc_docs = fc_video_docs * 2

    all_docs = fc_video_docs + cj_video_docs + pdf_docs
    db_general = FAISS.from_documents(all_docs, general_embeddings)
    db_in_depth = FAISS.from_documents(all_docs, in_depth_embeddings)

    cache_dir = dir.joinpath("cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    save_dir_general = cache_dir.joinpath("faiss_index_general")
    save_dir_in_depth = cache_dir.joinpath("faiss_index_in_depth")
    db_general.save_local(save_dir_general)
    db_in_depth.save_local(save_dir_in_depth)

    # copy results to cloud function
    dest_dir_general = dir.parent.parent.joinpath(
        "googlecloud/functions/getanswer/cache/faiss_index_general"
    )
    dest_dir_in_depth = dir.parent.parent.joinpath(
        "googlecloud/functions/getanswer/cache/faiss_index_in_depth"
    )
    shutil.copytree(save_dir_general, dest_dir_general, dirs_exist_ok=True)
    shutil.copytree(save_dir_in_depth, dest_dir_in_depth, dirs_exist_ok=True)

    logger.info(
        f"Combined database for general model created from all video URLs and PDF files saved to {save_dir_general}"
    )
    logger.info(
        f"Combined database for in-depth model created from all video URLs and PDF files saved to {save_dir_in_depth}"
    )
    return db_general, db_in_depth
