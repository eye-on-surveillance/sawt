import logging
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
import re

from api import RESPONSE_TYPE_DEPTH, RESPONSE_TYPE_GENERAL, RESPONSE_TYPE_VOTING

logger = logging.getLogger(__name__)


def remove_numbering_prefix(text):
    # Remove numbering prefixes like "1. ", "2. ", etc.
    return re.sub(r"^\d+\.\s+", "", text)


def get_in_depth_prompt_template(query):
    defining_prefixes = [
        "what is a",
        "define",
        "explain",
        "what do you know about",
        "tell me about",
        "give information on",
        "describe",
    ]
    defintion_template = """
        As an AI assistant, your task is to explain or define the term or concept "{question}" in the context of the provided transcripts from New Orleans City Council meetings in "{docs}".
        
        Your response should start with a concise explanation or definition of the term or concept. Then, highlight instances or discussions from the transcripts that help illustrate or contextualize the term or concept. If relevant, include any voting actions, but only provide information that is supported by the transcripts.
        
        Note: If the transcripts don't fully cover the scope of the question, it's fine to summarize the available details and state 'The provided documents might not cover all aspects of the question but they do provide some key insights on the following points: 
        Note: If the transcripts don't fully cover the scope of the question or the above-mentioned details are not present in the transcripts, state 'There is insufficient information available to answer this question accurately'.
    """

    general_template = """
        As a language model specifically trained on city council meetings, agendas, and minutes, your objective is to generate an in-depth response to "{question}", using data from the specified New Orleans City Council meeting documents in "{docs}". 
                
        Note: If the transcripts don't fully cover the scope of the question, it's fine to summarize the available details and state 'The provided documents do not cover all aspects of the question but they do provide some key insights on the following points: 
        Should the transcripts lack the relevant details entirely, state "The available information is insufficient for a comprehensive response to this question."
    """

    query = query.lower().strip()
    if any(query.startswith(prefix) for prefix in defining_prefixes):
        return defintion_template
    else:
        return general_template


def get_general_prompt_template(query):
    defining_prefixes = [
        "what is a",
        "define",
        "explain",
        "what do you know about",
        "tell me about",
        "give information on",
        "describe",
    ]
    defintion_template = """
        As an AI assistant, your task is to explain or define the term or concept "{question}" in the context of the provided transcripts from New Orleans City Council meetings in "{docs}".
        
        Note: Only use information contained in the provided transcripts. If the transcripts don't fully cover the scope of the question, it's fine to summarize the key points that are covered in relation to the question and state 'The provided documents might not cover all aspects of the question but they do provide some key insights on the following points: 
        Note: If the transcripts don't cover the scope of the question at all, state "There is insufficient information available to answer this question accurately"

    """
    general_template = """
        As an AI assistant, your task is to provide a general response to the question "{question}", using the provided transcripts from New Orleans City Council meetings in "{docs}".
        
        Note: Only use information contained in the provided transcripts. 
        Note: If the transcripts don't fully cover the scope of the question, it's fine to summarize the general key points provided in relation to the question and state 'The provided documents might not cover all aspects of the question but they do provide some key insights on the following points: 
        Note: If the transcripts don't cover the scope of the question at all, state "There is insufficient information available to answer this question accurately"
    """

    query = query.lower().strip()
    if any(query.startswith(prefix) for prefix in defining_prefixes):
        return defintion_template
    else:
        return general_template


def get_voting_prompt_template(query):
    voting_template = """
    As an AI assistant, your task is to analyze the transcripts from New Orleans City Council meetings provided in "{docs}" and detail the votes solely related to "{query}". Your response should strictly adhere to the information found within the transcripts, and not make assumptions or inferences.
    """
    return voting_template


def get_indepth_response_from_query(db, query, k=4):
    logger.info("Performing in-depth summary query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    template = get_in_depth_prompt_template(query)

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

    timestamps = [
        doc.metadata.get("timestamp", "Timestamp not available") for doc in docs
    ]

    urls = [doc.metadata.get("url", "Video URL not available") for doc in docs]

    final_response = ""
    for response, source, publish_date, timestamp, url in zip(
        generated_responses, generated_sources, publish_dates, timestamps, urls
    ):
        final_response += remove_numbering_prefix(response)
        final_response += (
            f"\n\nSource: {source} (Published on: {publish_date})\n{url}\n"
        )

        if timestamp != "Timestamp not available":
            final_response += f"Time: {timestamp}. Give or take 5 seconds.\n\n"

    return final_response


def get_general_summary_response_from_query(db, query, k=4):
    logger.info("Performing general summary query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    template = get_general_prompt_template(query)

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

    timestamps = [
        doc.metadata.get("timestamp", "Timestamp not available") for doc in docs
    ]

    urls = [doc.metadata.get("url", "Video URL not available") for doc in docs]

    final_response = ""
    for response, source, publish_date, timestamp, url in zip(
        generated_responses, generated_sources, publish_dates, timestamps, urls
    ):
        final_response += remove_numbering_prefix(response)
        final_response += (
            f"\n\nSource: {source} (Published on: {publish_date})\n{url}\n"
        )

        if timestamp != "Timestamp not available":
            final_response += f"Probably around {timestamp}. Note these times are very rough estimates based on word counts.\n\n"

    return final_response


def get_voting_summary_response_from_query(db, query, k=4):
    logger.info("Performing voting summary query using")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    template = get_voting_prompt_template(query)

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template=template,
    )

    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content)

    generated_responses = responses_llm.split("\n\n")

    generated_sources = [doc.metadata["source"] for doc in docs]

    pages = [doc.metadata["page"] for doc in docs]

    final_response = ""
    for response, source, page in zip(generated_responses, generated_sources, pages):
        final_response += remove_numbering_prefix(response)
        final_response += f"\n\nSource: {source}\n"
        final_response += f"Referenced from: Page {page}\n\n"

    return final_response


def route_question(db_general, db_in_depth, db_voting, query, query_type, k=4):
    if query_type == RESPONSE_TYPE_DEPTH:
        return get_indepth_response_from_query(db_in_depth, query, k)
    elif query_type == RESPONSE_TYPE_GENERAL:
        return get_general_summary_response_from_query(db_general, query, k)
    elif query_type == RESPONSE_TYPE_VOTING:
        return get_voting_summary_response_from_query(db_voting, query, k=4)
    else:
        raise ValueError(
            f"Invalid query_type. Expected {RESPONSE_TYPE_DEPTH} or {RESPONSE_TYPE_GENERAL}, got: {query_type}"
        )


def answer_query(
    query: str,
    response_type: str,
    db_general: any,
    db_in_depth: any,
    db_voting: any,
) -> str:
    final_response = route_question(
        db_general, db_in_depth, db_voting, query, response_type
    )

    return final_response
