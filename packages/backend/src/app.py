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
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

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

        loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=True)
        transcript = loader.load()
        logger.info(f"Transcript loaded for video URL: {video_url}")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        docs = text_splitter.split_documents(transcript)
        print(docs)

        all_docs.extend(docs)

    db = FAISS.from_documents(all_docs, embeddings)

    cache_dir = "cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    db.save_local(os.path.join(cache_dir, "faiss_index"))
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
        "url": "https://www.youtube.com/watch?v=XDMh4kiWRnM&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=b0zOzYK5Nvg&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=9uiSYTvYWBs&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=kyHwQ-8yXPc&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=aAE3-9byYYg&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=KZe2IU2VpU0&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=6-X1dXLVb84&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=JlbhsQ9kb0I&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=ZX00_-VUSrM&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=kqfTCmIlvjw&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=keVQuKFQExE&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=Sb2LWKCt1IM&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=sI6ttAClxKI&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=OZR01o_gXak&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=wamAbUcQ06s&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=XCLEd5zxC2o&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=B5ZOrOy3ZzQ&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=eDxRR8An03g&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=HYzqzJzS9zc&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=st0z9N9Zn5Y&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=c5gExu_qOeA&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=GTF6pyUhAFU&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=mLpe1Pp9-lQ&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=TUQ8MxcIWQI&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=VRdqvjz76-w&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=BdORXbpqGVI&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=UjjRKptF6QM&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=cKJm3hu-cL8&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=50nPsBXCnrg&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=I83StQ2nF4A&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=iRapue6Bgx4&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=mf1MnljjPvc&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=9PTtwGpfmbo&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=CRgme-Yh1yg&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=2DTyhHb90YU&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=4TXVbnbQReI&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=0FGxbwt66f0&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=sgST8k9xXsI&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=Ntm_NaIZvFE&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=RWFX5_stJss&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=xVZ-oOFqv70&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=uBjf7Mshx3A&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=-5X7bUC8qeU&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=lRIFLrozXk4&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=qTNPq_Gv5-E&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=1bEdJTtry-k&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=QiLMjqGrHOc&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=zdn-xkuc6y4&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=jcsll1fr6cU&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=1WzRXI5Wkzc&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=nBJtAqbFxKM&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=Q4HFI5CHa34&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=SlDa3tN2_Rc&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=w65XOQnAjM8&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=KiFnlChEBHw&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=p7qO1hT8CLA&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=p7qO1hT8CLA&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=TlEwLQxxxm4&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=kJ25K9fdVKc&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=Bl-Tv5yuUTw&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=MNUaOO3Pei0&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=q-Ts04cq1jI&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=95faDMjbrlE&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=cc-5P9EAtEA&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=7EoBFRwTaeE&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=rvQXZCFxgp8&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=ABsfv6bzOBA&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=7Nro7f26oEo&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=1NtrSv6iI8I&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=Cj-lbl_Y--o&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=WbeWxla4zUI&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=sRKCfArsTqA&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=VCHShl728y8&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=bTR53b05t50&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=yC5a099fbSU&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=U5AvDFjGvG8&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=re8yHWpkRO4&ab_channel=NewOrleansCityCouncil"
    },
    {
        "url": "https://www.youtube.com/watch?v=fxbVwYjIaok&ab_channel=NewOrleansCityCouncil"
    }
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


while True:
    query = input("Enter your query (or 'quit' to exit): ")
    if query == "quit":
        break

    response = answer_query(query)

print("Query memory:")
print(query_memory)
