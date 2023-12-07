# Sawt

Work in Progress

## Tulane Dev Integration Branch

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
  - [Embeddings creation](https://github.com/eye-on-surveillance/sawt/blob/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/packages/backend/src/preprocessor.py#L21)
  - [Sample tuning params](https://github.com/eye-on-surveillance/sawt/blob/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/packages/backend/src/preprocessor.py#L77)
- `packages/googlecloud`: Google Cloud Function invoked for every query
  - [Entry point](https://github.com/eye-on-surveillance/sawt/blob/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/packages/googlecloud/functions/getanswer/main.py#L20)
  - [K gets set](https://github.com/eye-on-surveillance/sawt/blob/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/packages/googlecloud/functions/getanswer/inquirer.py#L188)
  - [Construct response, all stored to DB](https://github.com/eye-on-surveillance/sawt/blob/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/packages/googlecloud/functions/getanswer/inquirer.py#L108)
  - [Deployment logic](https://github.com/eye-on-surveillance/sawt/blob/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/.github/workflows/main.yml)
- `packages/web`: NextJS web site
  - [DB migrations](https://github.com/eye-on-surveillance/sawt/tree/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/packages/web/supabase/migrations)
  - [Homepage](https://github.com/eye-on-surveillance/sawt/blob/3f9a17bdd6ee3f0ffe1a454a332f9d4d6f28086e/packages/web/app/page.tsx)
