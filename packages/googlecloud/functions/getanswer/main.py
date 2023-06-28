import logging
import time
import math

import google.cloud.logging
import functions_framework

from helper import parse_field
from inquirer import answer_query
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import LLMChain, HypotheticalDocumentEmbedder
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()

API_VERSION = "0.0.1"


def create_embeddings():
    llm = OpenAI()

    general_prompt_template = """
    As an AI assistant tasked with generating brief general summaries, your role is to provide succinct, balanced information from the transcripts of New Orleans City Council meetings in response to the question "{question}". The response should not exceed one paragraph in length. If the available information from the transcripts is insufficient to accurately summarize the issue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    in_depth_prompt_template = """
    As an AI assistant tasked with providing in-depth dialogical summaries, your role is to provide comprehensive information from the transcripts of New Orleans City Council meetings. Your response should mimic the structure of a real conversation, often involving more than two exchanges between the parties. The dialogue should recreate the actual exchanges that occurred between city council members and external stakeholders in response to the question "{question}". For specific queries related to any votes that took place, your response should include detailed information. This should cover the ordinance number, who moved and seconded the motion, how each council member voted, and the final outcome of the vote. For each statement, response, and voting action, provide a summary, followed by a direct quote from the meeting transcript to ensure the context and substance of the discussion is preserved. If a question is about the voting results on a particular initiative, include in your response how each council member voted, if they were present, and if there were any abstentions or recusals. Always refer back to the original transcript to ensure accuracy. If the available information from the transcripts is insufficient to accurately answer the question or recreate the dialogue, please respond with 'Insufficient information available.' If the question extends beyond the scope of information contained in the transcripts, state 'I don't know.'
    Answer:"""

    general_prompt = PromptTemplate(
        input_variables=["question"], template=general_prompt_template
    )
    in_depth_prompt = PromptTemplate(
        input_variables=["question"], template=in_depth_prompt_template
    )

    llm_chain_general = LLMChain(llm=llm, prompt=general_prompt)
    llm_chain_in_depth = LLMChain(llm=llm, prompt=in_depth_prompt)

    base_embeddings = OpenAIEmbeddings()

    general_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_general, base_embeddings=base_embeddings
    )
    in_depth_embeddings = HypotheticalDocumentEmbedder(
        llm_chain=llm_chain_in_depth, base_embeddings=base_embeddings
    )

    return general_embeddings, in_depth_embeddings


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
        print(f"Processing {response_type} query: {query}")
    else:
        raise ValueError("Unknown content type: {}".format(content_type))
    logging.info("Request parsed")

    general_embeddings, in_depth_embeddings = create_embeddings()
    answer = answer_query(query, response_type, general_embeddings, in_depth_embeddings)

    # return new uri
    end = time.time()
    elapsed = math.ceil(end - start)
    logging.info(f"Completed getanswer in {elapsed} seconds")
    print(f"\n\t--------- Completed getanswer in {elapsed} seconds --------\n")
    return (answer, 200, headers)
