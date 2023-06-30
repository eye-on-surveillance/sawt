# Getting started

```
cd functions
pip3.10 install -r getanswer/requirements.txt
python3.10 getanswer
```

## Running locally
[Docs](https://cloud.google.com/functions/docs/running/function-frameworks)

```
# Login to gcloud
gcloud auth login

# Set default app
gcloud auth application-default login

# Start function
OPENAI_API_KEY=XXX functions-framework --target=getanswer --debug

# Invoke function
curl -XPOST localhost:8080 -H "Content-Type: application/json" \
    -d '{"question":"Please outline instances where the police describe how often they use facial recognition and its results."}'
```

## Deploy

```
gcloud config set project the-great-inquirer

# https://cloud.google.com/functions/docs/configuring/memory
gcloud functions deploy getanswer \
    --gen2 \
    --runtime=python310 \
    --memory=4GB \
    --region=us-east1 \
    --source=. \
    --entry-point=getanswer \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars OPENAI_API_KEY=XXX

gcloud functions describe highlight-to-nft --gen2 --region us-east1 --format="value(serviceConfig.uri)"

curl -XPOST hhttps://getanswer-q5odwl64qa-ue.a.run.app \
    -H "Content-Type: application/json" \
    -d '{"question":"Outline concerns raised during the meeting? What were the responses to those concerns?","response_type":"general"}'
```

response_types = 'general' or 'in_depth'

**Note**: If OPENAI_API_KEY is set with quotes, `OPENAI_API_KEY='XXX'`, then the following work around could be used:

```
# https://github.com/openai/openai-python/issues/464#issuecomment-1593751169
import openai
import os
key = os.environ.get("OPENAI_API_KEY").replace("'", "")
openai.api_key = key
```