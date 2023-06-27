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

    if "ordinance" in query.lower():
        template = """
        As an AI assistant, your task is to provide an in-depth response to the question "{question}" focusing on the ordinance, using the provided transcripts from New Orleans City Council meetings in "{docs}".

        The response should include the following elements:
        1. A succinct summary of the ordinance, outlining its key points and potential implications.
        2. A balanced description of the discussion around the ordinance, including equal number of key points raised by City Council Members and external stakeholders.
        3. Direct quotes from City Council Members and external stakeholders to support the key points, ensuring equal representation from both sides.
        4. Details of any voting actions regarding the ordinance, such as who moved and seconded it, how each council member voted, and the final outcome. Include a quote from the meeting transcript to provide context.

        Note: If the transcripts do not provide sufficient information for any of the above points, simply skip the incomplete point and continue with the others. Only provide information based on available and verified data from the transcripts.
    """
    else:
        template = """
        As an AI assistant, your task is to generate an in-depth response to the question "{question}" using the transcripts from New Orleans City Council meetings provided in "{docs}". 

        Your response should resemble the structure of a real conversation, involving multiple exchanges between the parties. You should also include information about any voting actions that took place. 

        To format your response:
        1. Summarize a key point raised by a City Council Member.
        2. Provide a direct quote from the city council member that supports the key point. Prefix the quote with "Quote from City Council Member".
        3. Summarize a key point made by external stakeholders in response to the key point made by the City Council Member. 
        4. Provide a direct quote from the external stakeholder that supports the key point. Prefix the quote with "Quote from External Stakeholder". 
        5. Repeat steps 1-4 to ensure an equal representation of the City Council Members and external stakeholders.
        6. For any votes that took place during the discussion, summarize the voting action, including the ordinance number, who moved and seconded it, and how each council member voted. Accompany this summary with a direct quote from the meeting transcript.

        Note: If the transcripts do not provide sufficient information for any of the above points, simply skip that point and continue with the others. Only provide information that is supported by the transcripts.
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
        As an AI assistant, you have access to the transcripts from New Orleans City Council meetings and associated minutes and agendas provided in "{docs}".

        In response to the question "{question}", your primary task is to provide a balanced and comprehensive summary that equally represents information from the transcripts and minutes/agendas, as well as perspectives of both the City Council and external stakeholders.

        Your response should take the following format:

        1. A balanced summary of the City Council's position and external stakeholders' views on the issue based on the provided transcripts and minutes/agendas. 

        2. If the query is about a specific vote and the information is available, provide a balanced voting summary including the ordinance number, who moved and seconded it, how each council member voted, and any significant viewpoints from external stakeholders. 

        Your response should not exceed one paragraph and should equally represent information from the transcripts and minutes/agendas. 

        Note: If the available information from the transcripts and minutes/agendas is insufficient to accurately summarize the issue in a balanced manner, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts and minutes/agendas, state 'I don't know.'
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
