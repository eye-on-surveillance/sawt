import pandas as pd
import numpy as np
import requests
import csv
import json
from tqdm import tqdm

# Input CSV file with 'title' column
input_csv = "/Users/haydenoutlaw/Desktop/card_rows_export_2023-11-29.csv"
output_csv = "/Users/haydenoutlaw/Desktop/gpt4-varied-11-29.csv"

# point to getanswer server
api_endpoint = "http://localhost:8080"

# list of k values
k_list = [5, 10, 15]

# get response from local getanswer server, store answers
def make_api_call(title, k_inp):
    payload = {"query": title, "response_type": "in_depth", "card_id": 1, "k": k_inp}
    response = requests.post(f"{api_endpoint}", json=payload)
    rdict = json.loads(response.text)
    card_type_out = rdict["card_type"]
    citations_out = json.dumps(eval(str(rdict["citations"])))
    responses_out = json.dumps(eval(str(rdict["responses"])))
    return card_type_out, citations_out, responses_out, k_inp

# Open CSV file in append mode
with open(output_csv, 'a', newline='', encoding='utf-8') as csv_file:
    # define csv out file
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["query", "response_id", "card_type", "citations", "responses", "k"])
    
    # read inputs
    df = pd.read_csv(input_csv)


    print("Connected to getanswer at", api_endpoint)
    print("K Values", k_list)
    print("Generating Responses....")


    # for all queries, get answers and write out one at a time
    tqiter = enumerate(tqdm(df["title"]))
    for i, query in tqiter:
        for k_val in k_list:
            card_type, citations, responses, k = make_api_call(query, k_val)
            csv_writer.writerow([query, i, card_type, citations, responses, k])

print(f"Results saved to '{output_csv}'.")