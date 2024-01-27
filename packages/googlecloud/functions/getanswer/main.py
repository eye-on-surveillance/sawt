import logging
import time
import math

import google.cloud.logging
import functions_framework
from supabase import create_client
from dotenv import find_dotenv, load_dotenv
from helper import parse_field, get_dbs
from inquirer import answer_query
import os
import json

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

API_VERSION = "0.0.1"

db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()

# Setup Supabase client
load_dotenv(find_dotenv())


try:
    supabase_url = os.environ["SUPABASE_URL_PRODUCTION"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY_PRODUCTION"]
except KeyError:
    supabase_url = os.environ.get("SUPABASE_URL_STAGING")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY_STAGING")

if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL and key must be set in environment variables")

supabase = create_client(supabase_url, supabase_key)


def update_responses(response_chunk, card_id):
    try:
        current_data = supabase.table("cards").select("responses").eq("id", card_id).execute()

        if current_data.data and "response" in current_data.data[0]:
            existing_response = current_data.data[0]["response"]
            updated_response = existing_response + " " + response_chunk if existing_response else response_chunk
        else:
            updated_response = response_chunk

        supabase.table("cards").update({"responses": [{"response": updated_response}]}).eq("id", card_id).execute()
        logging.info("Response data successfully updated in Supabase")
    except Exception as e:
        logging.error(f"Failed to update Supabase responses: {e}")


def update_citations(citations, card_id, processing_time_ms):
    transformed_citations = [
        {
            "source_title": cit["Title"],
            "source_name": cit["Name"],
            "source_publish_date": cit["Published"],
            "source_url": cit["URL"],
            "source_page_number": cit["Page Number"],
        }
        for cit in citations
    ]

    try:
        supabase.table("cards").update(
            {
                "citations": transformed_citations,
                "processing_time_ms": processing_time_ms,
            }
        ).eq("id", card_id).execute()
    except Exception as e:
        logging.error(f"Failed to update Supabase citations: {e}")


@functions_framework.http
def getanswer(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        A success message and status, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    # Set CORS headers for the preflight request
    if request.method == "OPTIONS":
        # Allows POST requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }

        return ("", 204, headers)

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    logging.info(f"getanswer {API_VERSION}")
    start = time.time()

    # Parse args
    content_type = request.headers["Content-Type"]
    if content_type == "application/json":
        request_json = request.get_json(silent=True)
        logging.info(request_json)

        query = parse_field(request_json, "query")
        response_type = parse_field(request_json, "response_type")
        card_id = parse_field(request_json, "card_id")
    else:
        raise ValueError("Unknown content type: {}".format(content_type))

    logging.info("Request parsed")

    final_response = answer_query(
        query, response_type, voting_roll_df, db_fc, db_cj, db_pdf, db_pc, db_news
    )

    for response_chunk in final_response["responses"]:
        update_responses(response_chunk["response"], card_id)

    elapsed = int((time.time() - start) * 1000)
    update_citations(final_response["citations"], card_id, elapsed)

    logging.info(f"Completed getanswer in {elapsed} seconds")

    return ("Answer successfully submitted to Supabase", 200, headers)
