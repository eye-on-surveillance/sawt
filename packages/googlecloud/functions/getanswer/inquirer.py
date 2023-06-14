import logging
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from pathlib import Path
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

logger = logging.getLogger(__name__)
dir = Path(__file__).parent.absolute()


def get_response_from_query(db, query, k=4):
    """
    text-davinci-003 can handle up to 4097 tokens. Setting the chunksize to 1000 and k to 4 maximizes
    the number of tokens to analyze.
    """
    logger.info("Performing query...")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        As an AI assistant, you are to recreate the actual dialogue that occurred between city council members and law enforcement stakeholders, based on the transcripts from New Orleans City Council meetings provided in "{docs}".

        In response to the question "{question}", your output should mimic the structure of a real conversation, which often involves more than two exchanges between the parties. As such, please generate as many pairs of statements and responses as necessary to completely answer the query. 

        For each statement and response, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved. Your response should take the following format:

        1. Summary of Statement from City Council Member. After the summary, include a direct quote from the city council member that supports the summary. 
        2. Summary of Response or Statement from law enforcement stakeholders. After the summary, include a direct quote from the law enforcement stakeholder that supports the summary. 
        3. Continue this pattern, including additional statements and responses from both parties as necessary to provide a comprehensive answer.

        Note: If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
        
        """,
    )
    chain_llm = LLMChain(llm=llm, prompt=prompt)
    response_llm = chain_llm.run(question=query, docs=docs_page_content)

    chain_qa = load_qa_with_sources_chain(llm, chain_type="stuff")
    response_qa = chain_qa(
        {"input_documents": docs, "question": query}, return_only_outputs=True
    )

    return response_llm, response_qa, docs


def answer_query(query: str, embeddings: any) -> str:
    faiss_index_path = dir.joinpath("cache/faiss_index")
    db = FAISS.load_local(faiss_index_path, embeddings)
    logger.info("Loaded database from faiss_index")

    response_llm, response_qa, _ = get_response_from_query(db, query)

    final_response = f"{response_llm}\n\n\n{response_qa}"

    return final_response
