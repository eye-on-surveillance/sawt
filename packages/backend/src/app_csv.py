from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.csv_loader import CSVLoader
import os
import logging

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def answer_query(query: str) -> list[str]:
    logging.basicConfig(
        filename="query_log.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Initialize a list to store the responses
    responses = []

    csv_directory = "csv/"
    csv_files = [file for file in os.listdir(csv_directory) if file.endswith(".csv")]

    for csv_file in csv_files:
        logging.info(f"Processing file: {csv_file}")

        loader = CSVLoader(file_path=os.path.join(csv_directory, csv_file))

        index_creator = VectorstoreIndexCreator()
        docsearch = index_creator.from_loaders([loader])

        chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model_name="gpt-3.5-turbo"),
            chain_type="stuff",
            retriever=docsearch.vectorstore.as_retriever(),
            input_key="question",
        )

        logging.info(f"Querying '{csv_file}': {query}")
        response = chain({"question": query})

        logging.info(f"Result for '{csv_file}': {response['result']}")

        responses.append(response["result"])

    logging.info("Query processing complete.")

    return "\n".join(responses)
