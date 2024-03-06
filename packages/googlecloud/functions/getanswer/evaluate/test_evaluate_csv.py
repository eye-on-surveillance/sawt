"""
usage: 'deepeval test run test_evaluate_csv.py


This will read test queries from file inputted by user, then evaluate the responses according
to several metrics as implemented by the deepeval library <https://github.com/confident-ai/deepeval/> and gpt-3.5-turbo-1106

All hyperparameters used by current model are logged in deepeval login

"""
import pytest
import deepeval
import logging
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from deepeval import assert_test
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import AnswerRelevancyMetric, BiasMetric, ContextualRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from inquirer import route_question
from helper import get_dbs
from inquirer import INDEPTH_RESPONSE_LLM, INDEPTH_RESPONSE_PROMPT_TEMPLATE, INDEPTH_RESPONSE_K
from api import RESPONSE_TYPE_DEPTH

logger = logging.getLogger(__name__)


# model to use for evaluating responses
MODEL = 'gpt-3.5-turbo-1106'


def get_test_cases():
    """
    Run sawt on all test queries and create LLMTestCases for each.
    """
    test_cases = []
    db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()

    csv_file_name = input("Enter the name or path of your csv file of queries (ex: queries.csv):")
    if not os.path.exists(csv_file_name):
        print("\nThe file ", csv_file_name, " doesn't exist, check the path or name.")
        sys.exit()
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

    return EvaluationDataset(test_cases=test_cases)

dataset = get_test_cases()


@pytest.mark.parametrize(
    "test_case",
    dataset,
)
def test_dataset(test_case: LLMTestCase):
    ansRel = AnswerRelevancyMetric(threshold=0.2, model=MODEL)
    bias = BiasMetric(threshold=0.5, model=MODEL)
    contRel = ContextualRelevancyMetric(threshold=0.7, include_reason=True, model=MODEL)
    faithMet = FaithfulnessMetric(threshold=0.7, include_reason=True, model=MODEL)
   
    readability = GEval(name="Readability",
        criteria="Determine whether the text in 'actual output' is easy to read for those with a high school reading level.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        model=MODEL)


    punctuation = GEval(name="Punctuation",
        criteria="Determine whether the text in 'actual output' has proper punctuation.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        model=MODEL)
   
    opinions = GEval(name="Number of Opinions",
        criteria="Determine whether the text in 'actual output' expresses more than one opinion on the topic of the query.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        model=MODEL)

    assert_test(test_case, [ansRel, bias, contRel, faithMet,readability, punctuation, opinions])


# Log hyperparameters so we can compare across different test runs in deepeval login
@deepeval.log_hyperparameters(model=INDEPTH_RESPONSE_LLM.model_name, prompt_template=INDEPTH_RESPONSE_PROMPT_TEMPLATE.template)
def hyperparameters():
    return {'k': INDEPTH_RESPONSE_K}

