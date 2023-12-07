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

db_general, db_in_depth, voting_roll_df = get_dbs()

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

def update_supabase(responses, citations, card_id, processing_time_ms):
    transformed_citations = []
    for citation in citations:
        transformed_citations.append({
            "source_title": citation.get("Title"),
            "source_name": citation.get("Name"),
            "source_publish_date": citation.get("Published"),
            "source_url": citation.get("URL")
        })

    try:
        supabase.table("cards").update(
            {"responses": responses, 
             "citations": transformed_citations,
             "processing_time_ms": processing_time_ms}  # Update this line
        ).eq("id", card_id).execute()
        logging.info("Data successfully updated in Supabase")
    except Exception as e:
        logging.error(f"Failed to update Supabase: {e}")



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

    answer = answer_query(query, response_type, voting_roll_df, db_general, db_in_depth)

    try:
        answer = json.loads(answer)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse answer string to JSON: {e}")
        return ("Failed to process answer", 500, headers)

    print(f"Answer: {answer}")
    responses_data = answer.get("responses")
    
    print(f"Responses: {responses_data}")
    citations_data = answer.get("citations")

    print(f"Citations: {citations_data}")

    end = time.time()
    elapsed = int((end - start) * 1000)

    update_supabase(responses_data, citations_data, card_id, elapsed)
    logging.info(f"Completed getanswer in {elapsed} seconds")
    print(f"\n\t--------- Completed getanswer in {elapsed} seconds --------\n")

    return ("Answer successfully submitted to Supabase", 200, headers)



