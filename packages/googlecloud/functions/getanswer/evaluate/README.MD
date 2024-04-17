Using [confident-ai/deepeval](https://github.com/confident-ai/deepeval) LLM evaluation framework. 


Requires installation of deepeval library over pip:

'pip install -U deepeval'



For windows:
'set OPENAI_API_KEY=xxx' 

For OS:
'export OPENAI_API_KEY=xxx' 



To run tests:

test_evaluate_live.py 
    reads in a live test query from user input, gets the sawt response, evaluates the response according to several metrics as implemented by the deepeval library <https://github.com/confident-ai/deepeval/> and gpt-3.5-turbo-1106

    usage: 
        'deepeval test run test_evaluate_live.py'

test_evaluate_tsv.py
    reads test queries from tsv file inputted by user, gets the sawt responses, evaluates the responses according to several metrics as implemented by the deepeval library <https://github.com/confident-ai/deepeval/> and gpt-3.5-turbo-1106

    This file can contain be a gold data set with feature 'expected response', a list of queries without expected responses, or a mix of both. Queries with specified expected responses will be eveluated on 2 more metrics than queries without expected responses.

        usage: 
        'deepeval test run test_evaluate_tsv.py'

Test results and hyperparameters used by current model are logged in deepeval login