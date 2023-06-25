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
    """
    This function generates a detailed response (including direct quotes)
    of the dialogue between city council members and external stakeholders such as community members,
    civil servants, bureaucrats, law enforcement, etc.
    """
    logger.info("Performing in-depth query into public policy discussions...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
    As an AI assistant, your role is to recreate the actual dialogue that occurred between city council members and external stakeholders, based on the transcripts from New Orleans City Council meetings provided in "{docs}". In addition, also provide information about any votes that took place, such as the ordinance number, who moved and seconded it, and how each council member voted.

    In response to the question "{question}", your output should mimic the structure of a real conversation, which often involves more than two exchanges between the parties. 

    For each key point, response, and voting action, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved. 

    Your response should take the following format:
    1. Summarize a key point raised by City Council Member.
    2. Accompany this key point with a direct quote the city council member that supports the key point. Please prefix the quote with "Quote from City Council Member". 
    3. Summarize a key point made by external stakeholders in response to the key point made by the City Council Member. 
    4. Accompany this key point with a direct quote from the external stakeholder that supports the key point. Please prefix the quote with "Quote from External Stakeholder". 
    5. For any votes that took place during the discussion, summarize the voting action including the ordinance number, who moved and seconded it, and how each council member voted. Accompany this summary with a direct quote from the meeting transcript.
    6. Continue this pattern, for each key point, quote, and voting action until a comprehensive answer is reached.

    Note: If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content)

    generated_responses = responses_llm.split("\n\n")

    generated_titles = [doc.metadata["title"] for doc in docs]
    publish_dates = [doc.metadata["publish_date"].strftime("%Y-%m-%d") for doc in docs]

    final_response = ""
    for response, title, publish_date in zip(
        generated_responses, generated_titles, publish_dates
    ):
        final_response += (
            remove_numbering_prefix(response)
            + f"\n\nSource: {title} (Published on: {publish_date})\n\n"
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
        As an AI assistant, you have access to the transcripts from New Orleans City Council meetings provided in "{docs}".

        In response to the question "{question}", your primary task is to provide a comprehensive summary of the City Council's stance on the issue. Details of voting, including the ordinance number, who moved and seconded it, and how each council member voted should only be included if pertinent and available. Avoid recreating the dialogue. 

        Your response should take the following format:

        1. A comprehensive summary of City Council's position on the issue. 
        2. If the query is about a specific vote and the information is available, provide a voting summary including the ordinance number, who moved and seconded it, and how each council member voted. 

        Your response should not exceed one paragraph. 

        Note: If the available information from the transcripts is insufficient to accurately summarize the issue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
        """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content)

    return responses_llm


def route_question(db, query, query_type, k=4):
    if query_type == RESPONSE_TYPE_DEPTH:
        return get_indepth_response_from_query(db, query, k)
    elif query_type == RESPONSE_TYPE_GENERAL:
        return get_general_summary_response_from_query(db, query, k)
    else:
        raise ValueError(
            f"Invalid query_type. Expected {RESPONSE_TYPE_DEPTH} or {RESPONSE_TYPE_GENERAL}, got: {query_type}"
        )


def answer_query(query: str, response_type: str, embeddings: any) -> str:
    faiss_index_path = dir.joinpath("cache/faiss_index")
    db = FAISS.load_local(faiss_index_path, embeddings)
    logger.info("Loaded database from faiss_index")

    final_response = route_question(db, query, response_type)

    return final_response
