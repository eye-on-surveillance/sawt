import logging
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
import re
from itertools import zip_longest

from api import RESPONSE_TYPE_DEPTH, RESPONSE_TYPE_GENERAL

logger = logging.getLogger(__name__)


def get_indepth_response_from_query(db, query, k=4):
    logger.info("Performing in-depth summary query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])

    template = """
        As an AI assistant, your task is to provide an in-depth response to the "{question}", 
        using the provided transcripts from New Orleans City Council meetings here: "{docs}". Do not provide information about the votes.
        
        Note: If the transcripts don't fully cover the scope of the question, it's fine to highlight the key points that are covered and leave it at that.    
    """
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template=template,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content, temperature=0)

    generated_responses = responses_llm.split("\n\n")

    generated_titles = [
        doc.metadata.get("title", doc.metadata.get("source", "")) for doc in docs
    ]
    page_numbers = [doc.metadata.get("page_number") for doc in docs]
    generated_sources = [
        doc.metadata.get("source", "source not available") for doc in docs
    ]
    publish_dates = [
        doc.metadata.get("publish_date", "date not available") for doc in docs
    ]

    timestamps = [
        doc.metadata.get("timestamp", "timestamp not available") for doc in docs
    ]

    urls = [doc.metadata.get("url", "url not available") for doc in docs]

    final_response = ""
    for i, (
        response,
        title,
        page_number,
        source,
        publish_date,
        timestamp,
        url,
    ) in enumerate(
        zip_longest(
            generated_responses,
            generated_titles,
            page_numbers,
            generated_sources,
            publish_dates,
            timestamps,
            urls,
        )
    ):
        if response is None:
            response = "No response generated."
        else:
            response = response

        if i < k - 1:
            response += f"\n\nTitle: {title}"
            if page_number is not None:
                response += f"\nPage Number: {page_number}"
            response += f"\nSource: {source}\nPublished on: {publish_date}"
            if timestamp and timestamp != "Timestamp not available":
                response += f"\nApproximate timestamp of {timestamp} (±5 minutes margin of error)."
            if url and url != "URL not available":
                response += f"\nLink: {url}"

        final_response += response + "\n\n"

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

        Note: If the transcripts don't fully cover the scope of the question, it's fine to highlight the key points that are covered and leave it at that.    
        """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content, temperature=0)

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
