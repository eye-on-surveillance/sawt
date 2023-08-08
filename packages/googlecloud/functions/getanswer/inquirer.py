import logging
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
import json
import os

from helper import sort_retrived_documents
from api import RESPONSE_TYPE_DEPTH, RESPONSE_TYPE_GENERAL

logger = logging.getLogger(__name__)


def get_indepth_response_from_query(db, query, k):
    logger.info("Performing in-depth summary query...")
    llm = ChatOpenAI(model_name="gpt-4")

    doc_list = db.similarity_search_with_score(query, k=k)

    docs = sort_retrived_documents(doc_list)

    docs_page_content = " ".join([d[0].page_content for d in docs])

    template = """
        Transcripts: {docs}
        Question: {question}

        Using the information from the New Orleans city council {docs}, please explore the following question: {question}.
        Provide a balanced response that covers each aspect and person/organization mentioned in the transcripts that is relevant to the {question}.
        Please do not speculate in your response to the {question}.


        Ensure your response is based on the data found in the transcripts and, if applicable, is neutral in that you don't show any bias toward positivity or negativity in your response.
        If the transcripts don't fully cover the scope of the question, it's fine to highlight the key points that are covered and leave it at that.  
    """
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template=template,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content, temperature=0)

    generated_responses = responses_llm.split("\n\n")

    generated_titles = [
        doc[0].metadata.get("title", doc[0].metadata.get("source", "")) for doc in docs
    ]

    page_numbers = [doc[0].metadata.get("page_number") for doc in docs]
    generated_sources = [
        doc[0].metadata.get("source", "source not available") for doc in docs
    ]

    publish_dates = [
        doc[0].metadata.get("publish_date", "date not available") for doc in docs
    ]

    timestamps = [
        doc[0].metadata.get("timestamp", "timestamp not available") for doc in docs
    ]

    urls = [doc[0].metadata.get("url", "url not available") for doc in docs]

    def gen_responses(i):
        section = {}
        section["response"] = (
            generated_responses[i] if i < len(generated_responses) else None
        )
        section["source_title"] = (
            generated_titles[i] if i < len(generated_titles) else None
        )
        section["source_name"] = (
            os.path.basename(generated_sources[i])
            if i < len(generated_sources)
            else None
        )
        section["source_page_number"] = (
            page_numbers[i] if i < len(page_numbers) else None
        )
        section["source_publish_date"] = (
            publish_dates[i] if i < len(publish_dates) else None
        )
        section["source_timestamp"] = timestamps[i] if i < len(timestamps) else None
        section["source_url"] = urls[i] if i < len(urls) else None

        citation = {}
        if section["source_title"] is not None:
            citation["Title"] = section["source_title"]
        if section["source_publish_date"] is not None:
            citation["Published"] = section["source_publish_date"]
        if section["source_url"] is not None:
            citation["URL"] = section["source_url"]
        if section["source_timestamp"] is not None:
            citation["Video timestamp"] = section["source_timestamp"]
        if section["source_name"] is not None:
            citation["Name"] = section["source_name"]

        return section["response"], citation

    num_responses = len(generated_responses)

    responses = []
    citations = []

    for i in range(num_responses):
        response, citation = gen_responses(i)

        if response:
            responses.append({"response": response})

        if citation:
            citations.append(citation)

    card = {
        "card_type": RESPONSE_TYPE_DEPTH,
        "responses": responses,
        "citations": citations,
    }
    card_json = json.dumps(card)
    return card_json


def get_general_summary_response_from_query(db, query, k):
    logger.info("Performing general summary query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    prompt = PromptTemplate(
        input_variables=["question", "docs", "members"],
        template="""
        As an AI assistant, your task is to provide a general response to the question "{question}", using the provided transcripts from New Orleans City Council meetings in "{docs}".

        Guidelines for AI assistant: 
        - Derive responses from factual information found within the transcripts. 
        - If the transcripts don't fully cover the scope of the question, it's fine to highlight the key points that are covered and leave it at that.  
        """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content, temperature=0)
    response = {"response": responses_llm}
    card = {"card_type": RESPONSE_TYPE_GENERAL, "responses": [response]}
    card_json = json.dumps(card)
    return card_json


def route_question(db_general, db_in_depth, query, query_type, k=20):
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
