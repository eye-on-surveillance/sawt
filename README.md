# The Great Inquirer

Work in Progress

The Great Inquirer is a platform designed to facilitate direct communication between New Orleanians and their city council representatives. 

## Quickstart (no web)
1. `cd packages/backend && pip install -r requirements && python src`
2. `cd packages/googlecloud/functions && pip install -r requirements && python getanswer`

## Project structure
- `backend`: Preprocessor, only needs to be run once
- `web`: NextJS web site
- `googlecloud`: Google Cloud Function invoked for every query

## Getting started 
Follow the instructions below to run test locally 
```bash
# Pull data (transcripts, minutes, agendas) from the preprocessed stage using DVC
dvc pull

# Navigate to the 'src' directory inside 'packages/backend'
cd packages/backend/src

# Install the required Python dependencies
pip install -r requirements.txt

# Navigate to the 'getanswer' function directory inside 'packages/googlecloud/functions'
cd ../../googlecloud/functions/getanswer 

# Run the main Python script
python __main__.py
```