from langchain.vectorstores.faiss import FAISS
from pathlib import Path
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import LLMChain, HypotheticalDocumentEmbedder
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import logging


logger = logging.getLogger(__name__)


"""Parse field from JSON or raise error if missing"""


def parse_field(request_json, field: str):
    if request_json and field in request_json:
        return request_json[field]
    else:
        raise ValueError(f"JSON is invalid, or missing a '${field}' property")


def get_dbs():
    dir = Path(__file__).parent.absolute()
    general_embeddings, in_depth_embeddings, voting_embeddings = create_embeddings()

    general_faiss_index_path = dir.joinpath("cache/faiss_index_general")
    in_depth_faiss_index_path = dir.joinpath("cache/faiss_index_in_depth")
    voting_faiss_index_path = dir.joinpath("cache/faiss_index_voting")

    db_general = FAISS.load_local(general_faiss_index_path, general_embeddings)
    db_in_depth = FAISS.load_local(in_depth_faiss_index_path, in_depth_embeddings)
    db_voting = FAISS.load_local(voting_faiss_index_path, voting_embeddings)
    logger.info(
        "Loaded databases from faiss_index_general, faiss_index_in_depth, and faiss_index_voting"
    )
    return db_general, db_in_depth, db_voting


def create_embeddings():
    llm = OpenAI()

    general_prompt_template = """
    As an AI assistant, your role is to generate brief, concise summaries from the transcripts of New Orleans City Council meetings in response to the question "{question}". Please ensure the response is balanced and succinct, not exceeding one paragraph in length. If the transcripts do not provide enough information to accurately summarize the issue, please respond with 'Insufficient information available'. If the question extends beyond the scope of information contained in the transcripts, respond with 'I don't know'.
    Answer:"""

    in_depth_prompt_template = """
    As an AI assistant, your role is to provide comprehensive, dialogical summaries from the transcripts of New Orleans City Council meetings in response to the question "{question}". Your response should mimic a real conversation, often involving multiple exchanges between city council members and external stakeholders. If the transcripts do not provide enough information to accurately answer the question or recreate the dialogue, respond with 'Insufficient information available'. If the question extends beyond the scope of the transcripts, respond with 'I don't know'.
    Answer:"""

    voting_template = """
    As an AI assistant tasked with providing comprehensive information from the transcripts of New Orleans City Council meetings, your role is to respond to the "{question}", which may be related to a vote or briefs on an ordinance that took place. Your response should include detailed information as available, which might cover:

    - The ordinance number or reference (often prefixed with 'CAL. NO.' or 'MOTION – NO.')
    - The details of the ordinance or motion
    - Who introduced the ordinance or motion
    - Relevant discussion points or concerns raised
    - Any action taken, including votes, if any (specifying the yeas, nays, abstentions, absences, and recusals)
    - The final outcome of the vote or the current status of the ordinance or motion, if it has not been voted upon yet

    Always refer back to the original transcript to ensure accuracy. If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    general_prompt = PromptTemplate(
        input_variables=["question"], template=general_prompt_template
    )
    in_depth_prompt = PromptTemplate(
        input_variables=["question"], template=in_depth_prompt_template
    )

    voting_prompt = PromptTemplate(
        input_variables=["question"], template=voting_template
    )

    llm_chain_general = LLMChain(llm=llm, prompt=general_prompt)
    llm_chain_in_depth = LLMChain(llm=llm, prompt=in_depth_prompt)
    llm_chain_voting = LLMChain(llm=llm, prompt=voting_prompt)

    base_embeddings = OpenAIEmbeddings()

    general_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_general, base_embeddings=base_embeddings
    )
    in_depth_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_in_depth, base_embeddings=base_embeddings
    )
    voting_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_voting, base_embeddings=base_embeddings
    )

    return general_embeddings, in_depth_embeddings, voting_embeddings
