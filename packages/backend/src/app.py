import logging
import datetime
import os
import pickle
import hashlib
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
import textwrap

load_dotenv(find_dotenv())
embeddings = OpenAIEmbeddings()

# Set up logging configuration
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

cached_databases = {}  # Dictionary to store cached databases
CACHE_DIRECTORY = "cache"  # Cache directory name


def generate_cache_filename(video_url: str) -> str:
    # Generate an MD5 hash of the video URL
    md5_hash = hashlib.md5(video_url.encode()).hexdigest()

    # Create the cache directory if it doesn't exist
    if not os.path.exists(CACHE_DIRECTORY):
        os.makedirs(CACHE_DIRECTORY)

    return os.path.join(CACHE_DIRECTORY, f"{md5_hash}.pickle")


def load_content_from_cache(video_url: str) -> str:
    cache_file = generate_cache_filename(video_url)
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    return None


def save_content_to_cache(video_url: str, content: str) -> None:
    cache_file = generate_cache_filename(video_url)
    with open(cache_file, "wb") as f:
        pickle.dump(content, f)


def create_db_from_youtube_video_url(video_url: str) -> FAISS:
    logger.info(f"Loading video URL: {video_url}")

    # Check if the content is already cached
    cached_content = load_content_from_cache(video_url)
    if cached_content:
        logger.info(f"Using cached content for video URL: {video_url}")
        docs = cached_content
    else:
        loader = YoutubeLoader.from_youtube_url(video_url)
        transcript = loader.load()
        logger.info(f"Transcript loaded for video URL: {video_url}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        docs = text_splitter.split_documents(transcript)

        # Cache the content
        save_content_to_cache(video_url, docs)

    db = FAISS.from_documents(docs, embeddings)
    logger.info(f"Database created for video URL: {video_url}")

    # Cache the database
    cached_databases[video_url] = db

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


def answer_query(query: str) -> str:
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

    responses = []
    for i, video_info in enumerate(video_urls):
        video_url = video_info["url"]
        logger.info(f"Processing video URL: {video_url}")
        if video_url in cached_databases:
            db = cached_databases[video_url]
            logger.info(f"Using cached database for video URL: {video_url}")
        else:
            db = create_db_from_youtube_video_url(video_url)

        response, _ = get_response_from_query(db, query)
        responses.append(response)

        print(f"Response from video {i+1}:")
        print(textwrap.fill(response, width=85))
        print("=" * 85)
        logger.info(f"Response from video {i+1}:\n{response}\n{'=' * 85}")

    return "\n".join(responses)
