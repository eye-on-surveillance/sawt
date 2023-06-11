import logging
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from pathlib import Path

logger = logging.getLogger(__name__)
dir = Path(__file__).parent.absolute()


def get_response_from_query(db, query, k=4):
    """
    text-davinci-003 can handle up to 4097 tokens. Setting the chunksize to 1000 and k to 4 maximizes
    the number of tokens to analyze.
    """
    logger.info("Performing query...")
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    llm = ChatOpenAI(model_name="gpt-3.5-turbo")

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        As an assistant proficient in New Orleans City Council meetings, your task is to answer the question: {question}
        Use the video transcripts provided here: {docs}
        Your answers should only be based on the factual details from these transcripts. 
        If the details aren't sufficient to answer the question, please respond with "Insufficient information is contained in the transcripts."
        Your answer should be as comprehensive and detailed as possible.
        """,
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(question=query, docs=docs_page_content)
    response = response.replace("\n", "")
    return response, docs


def answer_query(query: str, embeddings: any) -> str:
    faiss_index_path = dir.joinpath("cache/faiss_index")
    db = FAISS.load_local(faiss_index_path, embeddings)
    logger.info("Loaded database from faiss_index")

    response, _ = get_response_from_query(db, query)

    return response
