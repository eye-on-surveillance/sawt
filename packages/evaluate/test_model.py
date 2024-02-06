import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, GEval, BaseMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

import os

openai_key = os.environ.get("OPENAI_API_KEY")



# Testing RAG relevancy
def test_answer_relevancy():

    retrieval_context = ["All customers are eligible for a 30 day full refund at no extra cost."]
    input = "What if these shoes don't fit?"
    actual_output = "We offer a 30-day full refund at no extra cost."

    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
    test_case = LLMTestCase(input=input, actual_output=actual_output, retrieval_context=retrieval_context)
    assert_test(test_case, [answer_relevancy_metric])

# Testing summarization
def test_summarization():
    input = "What if these shoes don't fit? I want a full refund."

    # Replace this with the actual output from your LLM application
    actual_output = "If the shoes don't fit, the customer wants a full refund."

    summarization_metric = GEval(
        name="Summarization",
        criteria="Summarization - determine if the actual output is an accurate and concise summarization of the input.",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.5
    )
    test_case = LLMTestCase(input=input, actual_output=actual_output)
    assert_test(test_case, [summarization_metric])




# Custom metric definition
class LengthMetric(BaseMetric):
    # This metric checks if the output length is greater than 10 characters
    def __init__(self, max_length: int=10):
        self.threshold = max_length

    def measure(self, test_case: LLMTestCase):
        self.success = len(test_case.actual_output) > self.threshold
        if self.success:
            score = 1
        else:
            score = 0
        return score

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Length"


def test_length():
    input = "What if these shoes don't fit?"

    # Replace this with the actual output of your LLM application
    actual_output = "We offer a 30-day full refund at no extra cost."
    length_metric = LengthMetric(max_length=10)
    test_case = LLMTestCase(input=input, actual_output=actual_output)
    assert_test(test_case, [length_metric])


    ## docs are extracted from inquirer.py as combined_docs_content, original_documents

    