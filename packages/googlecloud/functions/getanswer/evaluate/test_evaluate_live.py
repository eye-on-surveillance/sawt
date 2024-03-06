"""
usage: 'deepeval test run test_evaluate_live.py'

This will read a live test query from user input, get the sawt response, then evaluate the response according
to several metrics as implemented by the deepeval library <https://github.com/confident-ai/deepeval/> and gpt-3.5-turbo-1106

All hyperparameters used by current model are logged in deepeval login

"""
import pytest
import deepeval
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from deepeval import assert_test
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import AnswerRelevancyMetric, BiasMetric, ContextualRelevancyMetric, FaithfulnessMetric, GEval, SummarizationMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from inquirer import route_question
from helper import get_dbs
from inquirer import INDEPTH_RESPONSE_LLM, INDEPTH_RESPONSE_PROMPT_TEMPLATE, INDEPTH_RESPONSE_K
from api import RESPONSE_TYPE_DEPTH


# model to use for evaluating responses
MODEL = 'gpt-3.5-turbo-1106'


# test_cases = []
db_fc, db_cj, db_pdf, db_pc, db_news, voting_roll_df = get_dbs()

#get query from user input
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
test_case = LLMTestCase(input=query, actual_output=actual_output, retrieval_context=[retrieval_context])
# Initialize an evaluation dataset by supplying a list of test cases
dataset = EvaluationDataset(test_cases=[test_case])

# Loop through test cases using Pytest
@pytest.mark.parametrize(
    "test_case",
    dataset,
)
def test_live_query(test_case: LLMTestCase):
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
    assert_test(test_case, [bias, contRel, faithMet, readability, punctuation, opinions])

# Log hyperparameters so we can compare across different test runs in deepeval login
@deepeval.log_hyperparameters(model=INDEPTH_RESPONSE_LLM.model_name, prompt_template=INDEPTH_RESPONSE_PROMPT_TEMPLATE.template)
def hyperparameters():
    return {'k': INDEPTH_RESPONSE_K}