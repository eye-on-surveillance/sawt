import logging
import sys
import os

load_dotenv(find_dotenv("web/.env", raise_error_if_not_found=True))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))


from dotenv import find_dotenv, load_dotenv
from googlecloud.functions.getanswer.inquirer import answer_query
from googlecloud.functions.getanswer.helper import get_dbs
from googlecloud.functions.getanswer.api import RESPONSE_TYPE_DEPTH
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


def test_answer_relevancy():
    while True:


        raw_input = input("Enter your query with response type (or 'quit' to exit): ")
        if raw_input.lower() == "quit":
            break



        load_dotenv(find_dotenv("web/.env", raise_error_if_not_found=True))


        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
        )


        db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()
        #raw_input = "What was the most recent meeting about?"

        # Handling the query based on the response type
        actual_output, retrieval_context = answer_query(
            raw_input,
            RESPONSE_TYPE_DEPTH,
            voting_roll_df,
            db_fc,
            db_cj,
            db_pdf,
            db_pc,
            db_news,
            return_context = True
        )


        retrieval_context = [retrieval_context]

        # Replace this with the actual output of your LLM application
        #actual_output = "We offer a 30-day full refund at no extra cost."
        answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
        test_case = LLMTestCase(input=raw_input, actual_output=str(actual_output), retrieval_context=retrieval_context)
        assert_test(test_case, [answer_relevancy_metric])
        print("-="*10)