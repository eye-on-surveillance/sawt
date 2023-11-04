
import os
from dotenv import load_dotenv

def import_env_vars():
    os.chdir(r"packages\transcription")
    load_dotenv(r"cred\cred.env")

    # Get credentials from environment variables
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    GOOGLE_APPLICATION_CREDENTIALS= os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

    return { "YOUTUBE_API_KEY": YOUTUBE_API_KEY,
             "CLIENT_ID": CLIENT_ID,
             "CLIENT_SECRET": CLIENT_SECRET,
             "GOOGLE_APPLICATION_CREDENTIALS": GOOGLE_APPLICATION_CREDENTIALS
    }