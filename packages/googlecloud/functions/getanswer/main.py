import logging
import uuid
import time
import math

import google.cloud.logging
import functions_framework

from helper import parse_field
from inquirer import answer_query

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

API_VERSION = "0.0.1"

@functions_framework.http
def getanswer(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows POST requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    logging.info(f"getanswer {API_VERSION}")
    start = time.time()

    # Parse args
    content_type = request.headers["Content-Type"]
    if content_type == "application/json":
        request_json = request.get_json(silent=True)
        logging.info(request_json)

        query = parse_field(request_json, "query")
    else:
        raise ValueError("Unknown content type: {}".format(content_type))
    logging.info("Request parsed")
    answer = answer_query(query)

    # return new uri
    end = time.time()
    elapsed = math.ceil(end - start)
    logging.info(f"Completed getanswer in {elapsed} seconds")
    print(f"\n\t--------- Completed getanswer in {elapsed} seconds --------\n")
    return (answer, 200, headers)
