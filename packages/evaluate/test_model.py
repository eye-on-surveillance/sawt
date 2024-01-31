import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
import os

openai_key = os.environ.get("OPENAI_API_KEY")




def test_answer_relevancy():

    retrieval_context = ["All customers are eligible for a 30 day full refund at no extra cost."]
    input = "What if these shoes don't fit?"
    actual_output = "We offer a 30-day full refund at no extra cost."

    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
    test_case = LLMTestCase(input=input, actual_output=actual_output, retrieval_context=retrieval_context)
    assert_test(test_case, [answer_relevancy_metric])
