import logging
import sys
import os

import pytest
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv("web/.env.local", raise_error_if_not_found=True))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend/src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from googlecloud.functions.getanswer.inquirer import answer_query
from googlecloud.functions.getanswer.helper import get_dbs
from googlecloud.functions.getanswer.api import RESPONSE_TYPE_DEPTH
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, LatencyMetric
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric
from deepeval.metrics import SummarizationMetric
from deepeval.metrics import ContextualRelevancyMetric
from deepeval.metrics import BiasMetric
from deepeval.metrics import LatencyMetric
from deepeval import assert_test



#For Bias test - must run Run `pip install deepeval[bias]`
#to run tests run 'deepeval run tests test_model_baseline_tests.py

#get query from user input
def test_query():
    while True:
        raw_input = input("Enter your query (or type 'quit'): ")
        if raw_input.lower() == "quit":
            break
        
        actual_output, retrieval_context = get_response_and_context(raw_input)
       
        sum_test_case, sum_metric = summarization(actual_output, retrieval_context)
        assert_test(sum_test_case, [sum_metric])
        ans_rel_test_case, ans_rel_metric = answer_relevancy(raw_input, actual_output, retrieval_context)
        assert_test(ans_rel_test_case, [ans_rel_metric])
        faith_test_case, faith_metric = faithfulness(raw_input, actual_output, retrieval_context)
        assert_test(faith_test_case, [faith_metric])
        cont_rel_test_case, cont_rel_metric = contextual_relevancy(raw_input, actual_output, retrieval_context)
        assert_test(cont_rel_test_case, [cont_rel_metric])
        bias_test_case, bias_metric = bias(raw_input, actual_output, retrieval_context)
        assert_test(bias_test_case, [bias_metric])
        latency_test_case, latency_metric = latency(raw_input, actual_output)
        assert_test(latency_test_case, [latency_metric])



#get query response and retrieval context
def get_response_and_context(input):


    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    load_dotenv(find_dotenv("../../../web/.env.local", raise_error_if_not_found=True))
    db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()

    # Handling the query based on the response type
    actual_output, retrieval_context = answer_query(
        input,
        RESPONSE_TYPE_DEPTH,
        voting_roll_df,
        db_fc,
        db_cj,
        db_pdf,
        db_pc,
        db_news,
        return_context = True
    )


    response_parts = [response['response'] for response in actual_output['responses']]
    response_string = ' '.join(response_parts)

    return response_string, retrieval_context


#generates close-end yes or no questions for the retreival context and calculates the percentage of them that are a yes for both the response and retrieval context
def summarization(actual_output, retrieval_context):
    metric = SummarizationMetric(threshold=0.5)
    test_case = LLMTestCase(input=str(retrieval_context), actual_output=str(actual_output))
    return test_case, metric


def answer_relevancy(input, actual_output, retrieval_context):
    metric = AnswerRelevancyMetric(threshold=0.5)
    test_case = LLMTestCase(input=input, actual_output=str(actual_output), retrieval_context=[retrieval_context])
    return test_case, metric

# #evaluates whether the actual_output factually aligns with retrieval_context
def faithfulness(input, actual_output, retrieval_context):
    metric = FaithfulnessMetric(threshold=0.7, include_reason=True)
    test_case = LLMTestCase(input=input, actual_output=str(actual_output), retrieval_context=[retrieval_context])
    return test_case, metric

# #evaluates the overall relevance of the information presented in retrieval_context for the query
def contextual_relevancy(input, actual_output, retrieval_context):
    metric = ContextualRelevancyMetric(threshold=0.7, include_reason=True)
    test_case = LLMTestCase(input=input, actual_output=str(actual_output), retrieval_context=[retrieval_context])
    return test_case, metric

# #measures bias
def bias(input, actual_output, retrieval_context):
    metric = BiasMetric(threshold=0.5)
    test_case = LLMTestCase(input=input, actual_output=str(actual_output), retrieval_context=[retrieval_context])
    return test_case, metric


# #measures how long it takes a response to come back, aiming for 30 seconds
def latency(input, actual_output):

    metric = LatencyMetric(max_latency=30.0, include_reason=True)
    test_case = LLMTestCase(input=input, actual_output=str(actual_output), latency = 29.9)
    return test_case, metric
