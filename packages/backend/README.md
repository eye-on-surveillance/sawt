This is responsible for preprocessing the YouTube videos and creating a cache from them.
This cache is then supplied to Cloud Functions to query.

## Quickstart

```
# run commands from backend
cd backend

# Add OpenAPI key to .env
echo "OPENAI_API_KEY='sk-XXX'" >> .env

# Install dependencies
pip3.10 install -r requirements.txt

python3.10 src
```
