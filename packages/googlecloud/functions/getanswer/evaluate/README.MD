Using [confident-ai/deepeval](https://github.com/confident-ai/deepeval) LLM evaluation framework. 


Requires installation of deepeval library over pip:

'pip install -U deepeval'



For windows:
'export OPENAI_API_KEY=xxx' 

For OS:
'set OPENAI_API_KEY=xxx' 



To run tests:

test_evaluate_live.py 
    reads in a live test query from user input, gets the sawt response, evaluates the response according
    to several metrics as implemented by the deepeval library <https://github.com/confident-ai/deepeval/> and gpt-3.5-turbo-1106

    usage: 
        'deepeval test run test_evaluate_live.py'

test_evaluate_csv.py
    reads test queries from file inputted by user, gets the sawt response, evaluates the responses according
    to several metrics as implemented by the deepeval library <https://github.com/confident-ai/deepeval/> and gpt-3.5-turbo-1106

        usage: 
        'deepeval test run test_evaluate_csv.py'
