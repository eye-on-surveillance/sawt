import logging
import os
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAI
from pathlib import Path
import shutil
from langchain_experimental.text_splitter import SemanticChunker
from langchain.docstore.document import Document


logger = logging.getLogger(__name__)
dir = Path(__file__).parent.absolute()


def create_embeddings():
    llm = OpenAI()

    base_embeddings = OpenAIEmbeddings()

    general_prompt_template = """
    As an AI assistant, your role is to provide concise, balanced summaries from the transcripts of New Orleans City Council meetings in response to the user's query "{user_query}". Your response should not exceed one paragraph in length. If the available information from the transcripts is insufficient to accurately summarize the issue, respond with 'Insufficient information available.' If the user's query extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    in_depth_prompt_template = """
    As an AI assistant, use the New Orleans City Council transcript data that you were trained on to provide an in-depth and balanced response to the following query: "{user_query}" 
    Answer:"""

    general_prompt = PromptTemplate(
        input_variables=["user_query"], template=general_prompt_template
    )
    in_depth_prompt = PromptTemplate(
        input_variables=["user_query"], template=in_depth_prompt_template
    )

    # llm_chain_general = LLMChain(llm=llm, prompt=general_prompt)
    # llm_chain_in_depth = LLMChain(llm=llm, prompt=in_depth_prompt)

    # general_embeddings = HypotheticalDocumentEmbedder(
    #     llm_chain=llm_chain_general,
    #     base_embeddings=base_embeddings,
    # )

    # in_depth_embeddings = HypotheticalDocumentEmbedder(
    #     llm_chain=llm_chain_in_depth, base_embeddings=base_embeddings
    # )

    return base_embeddings, base_embeddings


def metadata_func_minutes_and_agendas(record: dict, metadata: dict) -> dict:
    metadata["title"] = record.get("title")
    metadata["page_number"] = record.get("page_number")
    metadata["publish_date"] = record.get("publish_date")
    return metadata


def create_db_from_minutes_and_agendas(doc_directory):
    logger.info("Creating database from minutes...")
    all_docs = []
    for doc_file in os.listdir(doc_directory):
        if not doc_file.endswith(".json"):
            continue
        doc_path = os.path.join(doc_directory, doc_file)
        loader = JSONLoader(
            file_path=doc_path,
            jq_schema=".messages[]",
            content_key="page_content",
            metadata_func=metadata_func_minutes_and_agendas,
        )

        data = loader.load()
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        for doc in data:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                new_doc = Document(page_content=chunk, metadata=doc.metadata)
                print(
                    f"Content: {new_doc.page_content}\nMetadata: {new_doc.metadata}\n"
                )
                all_docs.append(new_doc)
    logger.info("Finished database from minutes...")
    return all_docs


def metadata_news(record: dict, metadata: dict) -> dict:
    metadata["url"] = record.get("url")
    metadata["title"] = record.get("title")
    return metadata


def create_db_from_news_transcripts(news_json_directory):
    logger.info("Creating database from CJ transcripts...")
    all_docs = []
    for doc_file in os.listdir(news_json_directory):
        if not doc_file.endswith(".json"):
            continue
        doc_path = os.path.join(news_json_directory, doc_file)
        loader = JSONLoader(
            file_path=doc_path,
            jq_schema=".messages[]",
            content_key="page_content",
            metadata_func=metadata_news,
        )

        data = loader.load()
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        for doc in data:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                new_doc = Document(page_content=chunk, metadata=doc.metadata)
                print(
                    f"Content: {new_doc.page_content}\nMetadata: {new_doc.metadata}\n"
                )
                all_docs.append(new_doc)
    logger.info("Finished database from news transcripts...")
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
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        for doc in data:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                new_doc = Document(page_content=chunk, metadata=doc.metadata)
                print(
                    f"Content: {new_doc.page_content}\nMetadata: {new_doc.metadata}\n"
                )
                all_docs.append(new_doc)

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
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        for doc in data:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                new_doc = Document(page_content=chunk, metadata=doc.metadata)
                print(
                    f"Content: {new_doc.page_content}\nMetadata: {new_doc.metadata}\n"
                )
                all_docs.append(new_doc)
    logger.info("Finished database from news transcripts...")
    return all_docs


def create_db_from_public_comments(pc_json_directory):
    logger.info("Creating database from FC transcripts...")
    all_docs = []
    for doc_file in os.listdir(pc_json_directory):
        if not doc_file.endswith(".json"):
            continue
        doc_path = os.path.join(pc_json_directory, doc_file)
        loader = JSONLoader(
            file_path=doc_path,
            jq_schema=".messages[]",
            content_key="page_content",
            metadata_func=metadata_func,
        )

        data = loader.load()
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        for doc in data:
            chunks = text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                new_doc = Document(page_content=chunk, metadata=doc.metadata)
                print(
                    f"Content: {new_doc.page_content}\nMetadata: {new_doc.metadata}\n"
                )
                all_docs.append(new_doc)
    logger.info("Finished database from Public Comments...")
    return all_docs


def create_vector_dbs(
    fc_json_directory,
    cj_json_directory,
    doc_directory,
    pc_directory,
    news_directory,
    in_depth_embeddings,
):
    # Create databases from transcripts and documents
    fc_video_docs = create_db_from_fc_transcripts(fc_json_directory)
    cj_video_docs = create_db_from_cj_transcripts(cj_json_directory)
    pdf_docs = create_db_from_minutes_and_agendas(doc_directory)
    pc_docs = create_db_from_public_comments(pc_directory)
    news_docs = create_db_from_news_transcripts(news_directory)

    # Function to create, save, and copy FAISS index
    def create_save_and_copy_faiss(docs, embeddings, doc_type):
        # Create FAISS index
        db = FAISS.from_documents(docs, embeddings)

        cache_dir = dir.joinpath("cache")

        # Save locally
        local_save_dir = cache_dir.joinpath(f"faiss_index_in_depth_{doc_type}")
        db.save_local(local_save_dir)
        logger.info(f"Local FAISS index for {doc_type} saved to {local_save_dir}")

        # Copy to Google Cloud directory
        cloud_dir = dir.parent.parent.joinpath(
            f"googlecloud/functions/getanswer/cache/faiss_index_in_depth_{doc_type}"
        )
        shutil.copytree(local_save_dir, cloud_dir, dirs_exist_ok=True)
        logger.info(
            f"FAISS index for {doc_type} copied to Google Cloud directory: {cloud_dir}"
        )

        return db

    # Creating, saving, and copying FAISS indices for each document type
    faiss_fc = create_save_and_copy_faiss(fc_video_docs, in_depth_embeddings, "fc")
    faiss_cj = create_save_and_copy_faiss(cj_video_docs, in_depth_embeddings, "cj")
    faiss_pdf = create_save_and_copy_faiss(pdf_docs, in_depth_embeddings, "pdf")
    faiss_pc = create_save_and_copy_faiss(pc_docs, in_depth_embeddings, "pc")
    faiss_news = create_save_and_copy_faiss(news_docs, in_depth_embeddings, "news")

    # Return the FAISS indices
    return faiss_fc, faiss_cj, faiss_pdf, faiss_pc, faiss_news
