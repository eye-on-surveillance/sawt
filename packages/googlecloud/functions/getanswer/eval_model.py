import logging
import sys
import os



from dotenv import find_dotenv, load_dotenv
from inquirer import answer_query
from helper import get_dbs
from api import RESPONSE_TYPE_DEPTH

# Add the relative path of the directory where preprocessor.py is located
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/src"))

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv(find_dotenv("../../../web/.env", raise_error_if_not_found=True))


def main():
    query_memory = []
    db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()

    while True:
        query_input = input("Enter your query with response type (or 'quit' to exit): ")
        if query_input.lower() == "quit":
            break

        # Split the query_input into the response_type and the query
        query_parts = query_input.split(": ", 1)
        if len(query_parts) != 2:
            print("Invalid input format. Please use 'Response Type: Query'")
            continue

        response_type, query = query_parts

        # map response type to the required format
        response_type_map = {
            "In-Depth Response": RESPONSE_TYPE_DEPTH,
        }

        if response_type not in response_type_map:
            print(
                "Invalid response type. Please use 'In-Depth Response'."
            )
            continue

        # Handling the query based on the response type
        response= answer_query(
            query,
            response_type_map[response_type],
            voting_roll_df,
            db_fc,
            db_cj,
            db_pdf,
            db_pc,
            db_news,
            True
        )
        print("Output")
        print(response)
        print(len(response))
        query_memory.append(query)

    print("Query memory:")
    print(query_memory)


if __name__ == "__main__":
    main()
