import logging
import sys
import os

from dotenv import find_dotenv, load_dotenv
from inquirer import answer_query
from langchain.embeddings.openai import OpenAIEmbeddings

# Add the relative path of the directory where preprocessor.py is located
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend/src'))

# Now you should be able to import create_embeddings
from preprocessor import create_embeddings

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv(find_dotenv())


def main():
    query_memory = []
    general_embeddings, in_depth_embeddings = create_embeddings()

    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query == "quit":
            break

        response = answer_query(query, general_embeddings, in_depth_embeddings)
        print(response)
        query_memory.append(query)

    print("Query memory:")
    print(query_memory)


if __name__ == "__main__":
    main()
