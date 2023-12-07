## TU Capstone- Transcription

A generic API for fetching YouTube Audio and Transcripts.

#### Required Credentials   
    - YOUTUBE_API_KEY
    - GOOGLE_APPLICATION_CREDENTIALS
Create a cred folder containing cred.env variables according to dotenv configuration.

### transcripts.py
Retrieves & downloads the x-most recent video transcripts from a YouTube Channel.

### monitor.py
Retrieves & downloads the x-most recent video audio mp4s from a YouTube Channel. Future implemention should consider using Windows Task Scheduler to periodically monitor channel for new videos.

#### Oauth.py
Helper authentication function.


