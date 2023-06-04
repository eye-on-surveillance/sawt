from typing import List
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
import textwrap
import logging

load_dotenv(find_dotenv())
embeddings = OpenAIEmbeddings()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_db_from_youtube_video_urls(video_urls: List[dict]) -> FAISS:
    all_docs = []  
    for video_data in video_urls:
        video_url = video_data['url']
        logging.info(f"Processing video URL: {video_url}")
        loader = YoutubeLoader.from_youtube_url(video_url)
        transcript = loader.load()
        end_of_transcript = "\n--- End of Transcript ---"  
        transcript_with_metadata = f"{transcript}{end_of_transcript}"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(transcript_with_metadata)
        all_docs.extend(docs)  

    db = FAISS.from_documents(all_docs, embeddings)  
    return db


def get_response_from_query(db, query, k=4):
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    llm = OpenAI(model_name="text-davinci-003")

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        You are a helpful assistant that that can answer questions about New Orleans City Council meetings
        based on the provided Youtube transcripts.
        
        Answer the following question: {question}
        By searching the following video transcripts: {docs}
        
        Only use the factual information from the transcripts to answer the question.
        
        If you feel like you don't have enough information to answer the question, say "I don't know".
        
        Your response should be verbose and detailed.
        """,
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.run(question=query, docs=docs_page_content)
    response = response.replace("\n", "")
    return response, docs


if __name__ == "__main__":
    video_urls = [
        {"url": "https://www.youtube.com/watch?v=kqfTCmIlvjw&ab_channel=NewOrleansCityCouncil"},
        {"url": "https://www.youtube.com/watch?v=CRgme-Yh1yg&ab_channel=NewOrleansCityCouncil"},
        {"url": "https://www.youtube.com/watch?v=zdn-xkuc6y4&ab_channel=NewOrleansCityCouncil"},
        {"url": "https://www.youtube.com/watch?v=PwiJYkLNzZA&ab_channel=NewOrleansCityCouncil"},
        {"url": "https://www.youtube.com/watch?v=fxbVwYjIaok&ab_channel=NewOrleansCityCouncil"},
    ]

    logging.info("Creating database from YouTube video URLs...")
    db = create_db_from_youtube_video_urls(video_urls)

    query = "In the criminal justice committee meeting on December 12, 2022, what does Council Member Moreno say about surveillance?"
    logging.info(f"Query: {query}")

    response, docs = get_response_from_query(db, query)
    logging.info("Generated response:")
    logging.info(textwrap.fill(response, width=85))