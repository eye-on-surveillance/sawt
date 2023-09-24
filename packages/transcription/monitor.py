from googleapiclient.discovery import build
#import youtube_dl Has BEEN DEPRECATED BY GERMAN GOVERNMENT
import os
from dotenv import load_dotenv
from pytube import YouTube
import oauth
# Initialize the YouTube Data API client

env_vars = oauth.import_env_vars()
YOUTUBE_API_KEY = env_vars.get('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Specify the YouTube channel ID
channel_id = 'UC8oPEsQe9a0v6TdJ4K_QXoA' # New Orleans City Council

def get_latest_videos(channel_id, max_results=5): 
    """
    Fetches the latest x-number of videos from a YouTube channel.

    Args:
        channel_id (str): The ID of the YouTube channel to monitor.
        max_results (int): The maximum number of latest videos to fetch. Default is 5.

    Returns:
        list: A list of video IDs for the latest videos.
    """
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

def download_audio(video_ids):
    """
    Downloads the audio of a list of YouTube videos using pytube.

    Args:
        video_ids (list): A list of YouTube video IDs to download the audio for.

    Downloads: mp4 audio files of the desired Youtube videos.
    """
    for video_id in video_ids:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        ys = yt.streams.filter(only_audio=True).first()
        
        # Download the audio stream to the specified output path
        ys.download(output_path=r'\audio')

# Get the latest videos
video_ids = get_latest_videos(channel_id)

# Download the audio of the new videos
download_audio(video_ids)