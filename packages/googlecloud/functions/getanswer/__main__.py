import logging

from inquirer import answer_query
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import find_dotenv, load_dotenv

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv(find_dotenv())

def main():
    embeddings = OpenAIEmbeddings()
    query_memory = []

    while True:
        query = input("Enter your query (or 'quit' to exit): ")
        if query == "quit":
            break

        response = answer_query(query, embeddings)
        print(response)
        query_memory.append(query)

    print("Query memory:")
    print(query_memory)

if __name__ == "__main__":
    main()