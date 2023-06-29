import logging
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from pathlib import Path
import re

from api import RESPONSE_TYPE_DEPTH, RESPONSE_TYPE_GENERAL

logger = logging.getLogger(__name__)
dir = Path(__file__).parent.absolute()


def remove_numbering_prefix(text):
    # Remove numbering prefixes like "1. ", "2. ", etc.
    return re.sub(r"^\d+\.\s+", "", text)


def get_indepth_response_from_query(db, query, k=4):
    logger.info("Performing in-depth summary query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])

    template = """
        As an AI assistant, your task is to provide an in-depth response to the question "{question}", using the provided transcripts from New Orleans City Council meetings in "{docs}".

        Your response should resemble the structure of a real conversation and highlight key points from the discussion, including significant quotes from City Council Members and external stakeholders. If relevant, include any voting actions, but only provide information that is supported by the transcripts.
        
        Note: If the transcripts do not provide sufficient information for a detailed response, summarize the key points that are covered in the documents. If the question extends significantly beyond the scope of the provided documents, state 'The provided documents do not contain sufficient information to fully answer this question.'
    """

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template=template,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content)

    generated_responses = responses_llm.split("\n\n")

    generated_sources = [
        doc.metadata.get("title", doc.metadata.get("source", "")) for doc in docs
    ]
    publish_dates = [
        doc.metadata.get("publish_date", "Date not available") for doc in docs
    ]

    final_response = ""
    for response, source, publish_date in zip(
        generated_responses, generated_sources, publish_dates
    ):
        final_response += (
            remove_numbering_prefix(response)
            + f"\n\nSource: {source} (Published on: {publish_date})\n\n"
        )

    return final_response


def get_general_summary_response_from_query(db, query, k=4):
    logger.info("Performing general summary query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        As an AI assistant, your task is to provide a general response to the question "{question}", using the provided transcripts from New Orleans City Council meetings in "{docs}".

        Note: If the documents do not cover all aspects of the question, focus on summarizing the key points from the information available. In the event that the question is beyond the scope of the provided documents, please state 'The provided documents do not contain sufficient information to fully answer this question.'
        """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content)

    return responses_llm


def route_question(db_general, db_in_depth, query, query_type, k=4):
    if query_type == RESPONSE_TYPE_DEPTH:
        return get_indepth_response_from_query(db_in_depth, query, k)
    elif query_type == RESPONSE_TYPE_GENERAL:
        return get_general_summary_response_from_query(db_general, query, k)
    else:
        raise ValueError(
            f"Invalid query_type. Expected {RESPONSE_TYPE_DEPTH} or {RESPONSE_TYPE_GENERAL}, got: {query_type}"
        )


def answer_query(
    query: str, response_type: str, general_embeddings: any, in_depth_embeddings: any
) -> str:
    general_faiss_index_path = dir.joinpath("cache/faiss_index_general")
    in_depth_faiss_index_path = dir.joinpath("cache/faiss_index_in_depth")

    db_general = FAISS.load_local(general_faiss_index_path, general_embeddings)
    db_in_depth = FAISS.load_local(in_depth_faiss_index_path, in_depth_embeddings)

    logger.info("Loaded databases from faiss_index_general and faiss_index_in_depth")

    final_response = route_question(db_general, db_in_depth, query, response_type)

    return final_response
