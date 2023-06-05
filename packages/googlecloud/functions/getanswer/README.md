# Getting started
pip3 install -r requirements.txt

## Running locally
[Docs](https://cloud.google.com/functions/docs/running/function-frameworks)

```
# Login to gcloud
gcloud auth login

# Set default app
gcloud auth application-default login

# Start function
OPENAPI_API_KEY=XXX functions-framework --target=getanswer --debug

# Invoke function
curl -XPOST localhost:8080 -H "Content-Type: application/json" \
    -d '{"question":"Please outline instances where the police describe how often they use facial recognition and its results."}'
```

## Deploy

```
gcloud config set project the-great-inquirer

gcloud functions deploy getanswer \
    --gen2 \
    --runtime=python310 \
    --memory=1GB \
    --region=us-east1 \
    --source=. \
    --entry-point=getanswer \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars OPENAI_API_KEY='XXX'

gcloud functions describe highlight-to-nft --gen2 --region us-east1 --format="value(serviceConfig.uri)"

curl -XPOST hhttps://getanswer-q5odwl64qa-ue.a.run.app \
    -H "Content-Type: application/json" \
    -d '{"question":"Outline concerns raised during the meeting? What were the responses to those concerns?"}'
```