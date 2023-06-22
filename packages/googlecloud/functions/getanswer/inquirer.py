import logging
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from pathlib import Path
import re

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
    As an AI assistant, you are to recreate the actual dialogue that occurred between city council members and external stakeholders, based on the transcripts from New Orleans City Council meetings provided in "{docs}".

    In response to the question "{question}", your output should mimic the structure of a real conversation, which often involves more than two exchanges between the parties. As such, please generate as many pairs of statements and responses as necessary to completely answer the query. 

    For each key point and response, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved. Your response should take the following format:

    1. Summarize a key point raised by City Council Member. 
    2. Accompany this key point with a direct quote the city council member that supports the key point. Please prefix the quote with "Quote from City Council Member". 
    3. Summarize a key point made by external stakeholders in response to the key point made by the City Council Member. 
    4. Accompany this key point with a direct quote from the external stakeholder that supports the key point. Please prefix the quote with "Quote from External Stakeholder". 
    5. Continue this pattern, for each key point and each quote from both parties, until a comprehensive answer is reached.

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
            + f"\n\nSourced from Youtube: {title} (Published on: {publish_date})\n\n"
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

        In response to the question "{question}", provide a succinct summary of the City Council's stance on the issue. Avoid recreating the dialogue. 

        Your response should take the following format:

        1. Overview of City Council's position.

        Note: If the available information from the transcripts is insufficient to accurately answer the question or summarize the issue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
        """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    responses_llm = chain_llm.run(question=query, docs=docs_page_content)

    return responses_llm


def route_question(db, query, k=4):
    if query.startswith("Provide a detailed report"):
        return get_indepth_response_from_query(db, query, k)
    else:
        return get_general_summary_response_from_query(db, query, k)


def answer_query(query: str, embeddings: any) -> str:
    faiss_index_path = dir.joinpath("cache/faiss_index")
    db = FAISS.load_local(faiss_index_path, embeddings)
    logger.info("Loaded database from faiss_index")

    final_response = route_question(db, query)

    return final_response
