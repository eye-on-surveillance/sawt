"""
usage: OPENAI_API_KEY=xxx python evaluate.py

This will read test queries from queries.csv or take a live query, get the sawt response, then evaluate the response according
to several metrics as implemented by the deepeval library <https://github.com/confident-ai/deepeval/>

"""
import pytest
import deepeval
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import BaseMetric, GEval, AnswerRelevancyMetric

import deepeval
import logging
import sys
import os
from dotenv import find_dotenv, load_dotenv
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import csv
from deepeval import assert_test, evaluate
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import AnswerRelevancyMetric, BiasMetric, ContextualRelevancyMetric, FaithfulnessMetric, GEval, SummarizationMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from inquirer import route_question
from helper import get_dbs
from inquirer import INDEPTH_RESPONSE_LLM, INDEPTH_RESPONSE_PROMPT_TEMPLATE, INDEPTH_RESPONSE_K
# from helper import indepth_response_prompt_template
# from helper import indepth_resonse_k
from api import RESPONSE_TYPE_DEPTH
from tqdm import tqdm

logger = logging.getLogger(__name__)

# model to use for evaluating responses
MODEL = 'gpt-3.5-turbo-1106'

#command line flags
parser = argparse.ArgumentParser()
parser.add_argument("-l", action='store_true',
                    help="Option to input query on command line.")

parser.add_argument("-d", action='store_true',
                    help="Option to give a csv file of queries.")
args = parser.parse_args()

l = args.l
d = args.d



def get_test_cases():
    """
    Run sawt on all test queries and create LLMTestCases for each.
    """
    test_cases = []
    db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()

    if not l and not d:
        print("Error: include either '-l' for a live query or -d for a csv file of queries with the command.")
        sys.exit()

    if l:
        query = input("Enter your query: ")
        
        (actual_output, retrieval_context) = route_question(
            voting_roll_df,
            db_fc,
            db_cj,
            db_pdf,
            db_pc,
            db_news,
            query,
            RESPONSE_TYPE_DEPTH,
            k=INDEPTH_RESPONSE_K,
            return_context=True
        )

        actual_output = ' '.join(i['response'] for i in actual_output['responses'])    
        test_cases.append(LLMTestCase(input=query, actual_output=actual_output, retrieval_context=[retrieval_context]))
    else:
        pass

    if d:
        csv_file_name = input("Enter the name or path of your csv file of queries (ex: queries.csv):")
        logger.info('generating answers to all test queries...')

        for query in open(csv_file_name):
            query = query.strip()
            actual_output, retrieval_context = route_question(
                voting_roll_df,
                db_fc,
                db_cj,
                db_pdf,
                db_pc,
                db_news,
                query,
                RESPONSE_TYPE_DEPTH,
                k=5,
                return_context=True
            )
            # get single string for text response.
            actual_output = ' '.join(i['response'] for i in actual_output['responses'])    
            test_cases.append(LLMTestCase(input=query, actual_output=actual_output, retrieval_context=[retrieval_context]))
    elif not os.path.exists(d):
        print("\nThe file ", csv_file_name, " doesn't exist, check the path or name.")
        sys.exit()
    else:
        pass

    return EvaluationDataset(test_cases=test_cases)


dataset = get_test_cases()

dataset.evaluate([
                    SummarizationMetric(threshold=0.5, include_reason=True, model=MODEL),
                    AnswerRelevancyMetric(threshold=0.2, model=MODEL),
                    BiasMetric(threshold=0.5, model=MODEL),
                    ContextualRelevancyMetric(threshold=0.7, include_reason=True, model=MODEL),
                    FaithfulnessMetric(threshold=0.7, include_reason=True, model=MODEL),
                    
                    GEval(name="Readability",
                        criteria="Determine whether the text in 'actual output' is easy to read for those with a high school reading level.",
                        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
                        model=MODEL),

                    GEval(name="Punctuation",
                        criteria="Determine whether the text in 'actual output' has proper punctuation.",
                        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
                        model=MODEL),
                    
                    GEval(name="Number of Opinions",
                        criteria="Determine whether the text in 'actual output' expresses all major opinions on the topic of the query.",
                        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
                        model=MODEL)
                  ])

# def test_coherence():
#     coherence_metric = GEval(
#         name="Coherence",
#         criteria="Coherence - determine if the actual output is logical, has flow, and is easy to understand and follow.",
#         evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
#         threshold=0.5,
#     )
#     test_case = LLMTestCase(
#         input="What if these shoes don't fit? I want a full refund.",
#         # Replace this with the actual output from your LLM application
#         actual_output="If the shoes don't fit, the customer wants a full refund.",
#     )
#     assert_test(test_case, [coherence_metric])

# Log hyperparameters so we can compare across different test runs in deepeval login
@deepeval.log_hyperparameters(model=INDEPTH_RESPONSE_LLM.model_name, prompt_template=INDEPTH_RESPONSE_PROMPT_TEMPLATE.template)
def hyperparameters():
    return {'temperature':0, 'k': INDEPTH_RESPONSE_K}