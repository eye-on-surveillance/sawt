import logging
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
import re

from api import RESPONSE_TYPE_DEPTH, RESPONSE_TYPE_GENERAL

logger = logging.getLogger(__name__)


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

        Your response should resemble the structure of a real conversation and highlight key points from the discussion. If relevant, include any voting actions, but only provide information that is supported by the transcripts.
        
        Note: If the transcripts don't fully cover the scope of the question, it's fine to highlight the key points that are covered and state 'The provided documents might not cover all aspects of the question but they do provide some key insights on the following points:'.    """

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

        Note: If the transcripts don't fully cover the scope of the question, it's fine to highlight the key points that are covered and state 'The provided documents might not cover all aspects of the question but they do provide some key insights on the following points:'.    
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
    query: str, response_type: str, db_general: any, db_in_depth: any
) -> str:
    final_response = route_question(db_general, db_in_depth, query, response_type)

    return final_response
