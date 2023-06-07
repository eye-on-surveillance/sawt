import logging
import datetime
import os
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
import textwrap

load_dotenv(find_dotenv())
embeddings = OpenAIEmbeddings()

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

query_memory = []


def create_db_from_youtube_urls(video_urls) -> FAISS:
    all_docs = []
    for video_info in video_urls:
        video_url = video_info["url"]
        logger.info(f"Processing video URL: {video_url}")

        loader = YoutubeLoader.from_youtube_url(video_url)
        transcript = loader.load()
        logger.info(f"Transcript loaded for video URL: {video_url}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        docs = text_splitter.split_documents(transcript)

        all_docs.extend(docs)

    db = FAISS.from_documents(all_docs, embeddings)

    db.save_local("cache/faiss_index")
    logger.info("Combined database created from all video URLs")
    return db


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


video_urls = [
    {
        "url": "https://www.youtube.com/watch?v=kqfTCmIlvjw&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=CRgme-Yh1yg&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=zdn-xkuc6y4&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=PwiJYkLNzZA&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=fxbVwYjIaok&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=8moPWzrdPiQ&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=bEhdi86jsuY&ab_channel=NewOrleansCityCouncil"
    },
]


def answer_query(query: str) -> str:
    faiss_index_path = "cache/faiss_index"
    if os.path.exists(faiss_index_path):
        db = FAISS.load_local(faiss_index_path, embeddings)
        logger.info("Loaded database from faiss_index")
    else:
        db = create_db_from_youtube_urls(video_urls)

    response, _ = get_response_from_query(db, query)
    print("Bot response:")
    print(textwrap.fill(response, width=85))
    print()

    query_memory.append(query)
    return response


# while True:
#     query = input("Enter your query (or 'quit' to exit): ")
#     if query == "quit":
#         break

#     response = answer_query(query)

# print("Query memory:")
# print(query_memory)
