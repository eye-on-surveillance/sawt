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
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")

    docs = db.similarity_search(query, k=k)

    docs_page_content = " ".join([d.page_content for d in docs])
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        You are a helpful assistant that can answer questions about New Orleans City Council meetings 
        based on the provided Youtube transcripts.
        
        Answer the following question: {question}
        By searching the following video transcripts: {docs}
        
        Your response should be verbose and detailed. Please review the metadata and include the title of the video in the last sentence.
        Also, please provide at least one direct quote. 
        Only use the factual information from the transcripts to answer the question.
        
        If you feel like you don't have enough information to answer the question, say "I don't know".
        
      

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
