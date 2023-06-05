import logging
import csv
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
import textwrap
import datetime
import os

import google.cloud.logging
logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

embeddings = OpenAIEmbeddings()

def create_db_from_youtube_video_url(video_url: str) -> (FAISS, list):
    logging.info(f"Loading video URL: {video_url}")
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()
    logging.info(f"Transcript loaded for video URL: {video_url}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(transcript)

    db = FAISS.from_documents(docs, embeddings)
    logging.info(f"Database created for video URL: {video_url}")
    return db, docs


def write_docs_to_csv(docs, filename):
    directory = os.path.join(os.path.dirname(__file__), "csv")
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, filename)

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for doc in docs:
            writer.writerow([doc])


def get_response_from_query(db, query, k=4):
    """
    text-davinci-003 can handle up to 4097 tokens. Setting the chunksize to 1000 and k to 4 maximizes
    the number of tokens to analyze.
    """
    logging.info("Performing query...")
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    llm = OpenAI(model_name="text-davinci-003")

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        You are a helpful assistant that can answer questions about New Orleans City Council meetings
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


def answer_question(question: str) -> str:
    video_urls = [
        {
            "url": "https://www.youtube.com/watch?v=kqfTCmIlvjw&ab_channel=NewOrleansCityCouncil"
        },
        # {
        #     "url": "https://www.youtube.com/watch?v=CRgme-Yh1yg&ab_channel=NewOrleansCityCouncil"
        # },
        # {
        #     "url": "https://www.youtube.com/watch?v=zdn-xkuc6y4&ab_channel=NewOrleansCityCouncil"
        # },
        # {
        #     "url": "https://www.youtube.com/watch?v=PwiJYkLNzZA&ab_channel=NewOrleansCityCouncil"
        # },
        # {
        #     "url": "https://www.youtube.com/watch?v=fxbVwYjIaok&ab_channel=NewOrleansCityCouncil"
        # },
        # {
        #     "url": "https://www.youtube.com/watch?v=8moPWzrdPiQ&ab_channel=NewOrleansCityCouncil"
        # },
        # {
        #     "url": "https://www.youtube.com/watch?v=bEhdi86jsuY&ab_channel=NewOrleansCityCouncil"
        # },
    ]

    databases = []
    for i, video_info in enumerate(video_urls):
        video_url = video_info["url"]
        logging.info(f"Processing video URL: {video_url}")
        db, docs = create_db_from_youtube_video_url(video_url)
        databases.append(db)

        csv_filename = f"docs_{i+1}.csv"
        # write_docs_to_csv(docs, csv_filename)
        print(f"CSV file created for video {i+1}: {csv_filename}")

    responses = []
    for i, db in enumerate(databases):
        logging.info(f"Processing query for video {i+1}")
        response, _ = get_response_from_query(db, question)
        responses.append(response)

        print(f"Response from video {i+1}:")
        print(textwrap.fill(response, width=85))
        print("=" * 85)
        logging.info(f"Response from video {i+1}:\n{response}\n{'=' * 85}")

    return "\n".join(responses)
