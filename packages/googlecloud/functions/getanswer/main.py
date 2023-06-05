import logging
import uuid
import time
import math

import google.cloud.logging
import functions_framework

from helper import parse_field
from inquirer import answer_question
logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

API_VERSION = '0.0.1'

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
    logging.info(f'getanswer {API_VERSION}')
    start = time.time()

    # Parse args
    content_type = request.headers['content-type']
    if content_type == 'application/json':
        request_json = request.get_json(silent=True)
        logging.info(request_json)

        question = parse_field(request_json, 'question')
    else:
        raise ValueError("Unknown content type: {}".format(content_type))
    logging.info("Request parsed")
    answer = answer_question(question)

    # return new uri
    end = time.time()
    elapsed = math.ceil(end - start)
    logging.info(f"Completed getanswer in {elapsed} seconds")
    print(f"\n\t--------- Completed getanswer in {elapsed} seconds --------\n")
    return answer