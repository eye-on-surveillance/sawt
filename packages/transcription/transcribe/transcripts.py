from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import oauth
import json
import os

# Get credentials from environment variables
env_vars = oauth.import_env_vars()
YOUTUBE_API_KEY = env_vars.get("YOUTUBE_API_KEY")
CLIENT_ID       = env_vars.get("CLIENT_ID")
CLIENT_SECRET   = env_vars.get("CLIENT_SECRET")
GOOGLE_APPLICATION_CREDENTIALS= env_vars.get("GOOGLE_APPLICATION_CREDENTIALS")

def get_latest_videos(channel_id, max_results=5): 

    """
    Fetches the latest x-number of videos from a YouTube channel.

    Args:
        channel_id (str): The ID of the YouTube channel to monitor.
        max_results (int): The maximum number of latest videos to fetch. Default is 5.

    Returns:
        list: A list of video IDs for the latest videos.
    """
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # Fetch channel details to get the ID of the uploads playlist
    request = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    )
    response = request.execute()

    if not response.get('items'):
        raise ValueError(f"No channel found with ID {channel_id}")
    
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()
    
    video_ids = [item['snippet']['resourceId']['videoId'] for item in response['items']]
    
    return video_ids

def download_transcripts(video_ids):
    for video_id in video_ids:
        try:
            # Grabs transcript for the video
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            print(transcript)
            with open(f'transcripts-data\\YT_transcripts\\{video_id}_transcript.json', 'w+', encoding='utf-8') as file:
                  json.dump(transcript, file)

            print(f'Transcript for {video_id} saved successfully.')

        except Exception as e:
            print(f'An error occurred while fetching the transcript for {video_id}: {e}')

channel_id = "UC8oPEsQe9a0v6TdJ4K_QXoA"
video_ids = get_latest_videos(channel_id, 10)
download_transcripts(video_ids)