import logging
import sys
import os



from dotenv import find_dotenv, load_dotenv
from .inquirer import answer_query
from .helper import get_dbs
from .api import RESPONSE_TYPE_DEPTH
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
import csv


def test_answer_relevancy():

    load_dotenv(find_dotenv("../../../web/.env", raise_error_if_not_found=True))
    sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/src"))
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    test_cases_csv = "test_cases.csv"

    db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()

    with open(test_cases_csv, 'r') as file:
        csv_reader = csv.reader(file)

        headers = next(csv_reader)

        for row in csv_reader:
            raw_input, response_type, evaluation_goal = row[0], row[1], row[2]
        
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


            if evaluation_goal == "AnswerRelevancy":
                eval_metric = AnswerRelevancyMetric(threshold=0.2)

            test_case = LLMTestCase(input=raw_input, actual_output=str(actual_output), retrieval_context=retrieval_context)
            assert_test(test_case, [eval_metric])