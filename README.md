# Sawt

Work in Progress

Sawt is a tool designed to bridge the communication gap between New Orleanians and their city council representatives.

## Prerequisites

- Install [DVC](https://dvc.org/doc/install)

## Quickstart

1. Pull data: `dvc pull`
1. Start cloud function locally:

```
cd packages/googlecloud/functions
pip install -r requirements.txt
OPENAI_API_KEY=sk-XXX functions-framework --target=getanswer --debug
```

1. Get answer:

```
curl -XPOST http://localhost:8080 -v -H "Content-Type: application/json" \
    -d '{"query":"Is surveillance effective?","response_type":"in_depth"}'
```

## Project structure

- `packages/backend`: Preprocessor, only needs to be run once
- `packages/googlecloud`: Google Cloud Function invoked for every query
- `packages/web`: NextJS web site
