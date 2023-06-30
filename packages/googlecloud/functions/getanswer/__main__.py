import logging
import sys
import os

from dotenv import find_dotenv, load_dotenv
from inquirer import answer_query
from langchain.embeddings.openai import OpenAIEmbeddings
from helper import get_dbs

# Add the relative path of the directory where preprocessor.py is located
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/src"))

# Now you should be able to import create_embeddings

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv(find_dotenv())


def main():
    query_memory = []
    db_general, db_in_depth = get_dbs()

    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query == "quit":
            break

        response = answer_query(query, db_general, db_in_depth)
        print(response)
        query_memory.append(query)

    print("Query memory:")
    print(query_memory)


if __name__ == "__main__":
    main()
