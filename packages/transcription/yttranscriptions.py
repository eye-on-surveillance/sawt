from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import oauth
import json
import os

class YouTubeTranscriptions:
    def __init__(self):
        # Get credentials from environment variables
        env_vars = oauth.import_env_vars()
        self.YOUTUBE_API_KEY = env_vars.get("YOUTUBE_API_KEY")
        self.CLIENT_ID       = env_vars.get("CLIENT_ID")
        self.CLIENT_SECRET   = env_vars.get("CLIENT_SECRET")
        self.GOOGLE_APPLICATION_CREDENTIALS= env_vars.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.youtube = build('youtube', 'v3', developerKey=self.YOUTUBE_API_KEY)

    def get_latest_videos(self, channel_id, max_results=5): 
        """
        Fetches the latest x-number of videos from a YouTube channel.

        Args:
            channel_id (str): The ID of the YouTube channel to monitor.
            max_results (int): The maximum number of latest videos to fetch. Default is 5.

        Returns:
            list: A list of video IDs for the latest videos.
        """
        youtube = build('youtube', 'v3', developerKey=self.YOUTUBE_API_KEY)

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

    def download_transcripts(self, video_ids):
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
    
        def download_audio(self, video_ids, audio_path):
            for video_id in video_ids:
                yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
                ys = yt.streams.filter(only_audio=True).first()
                
                # Download the audio stream to the specified output path
                print(f'Downloading audio for {video_id}...')
                ys.download(output_path=audio_path, filename=video_id+".mp4")
                print(f'Audio for {video_id} downloaded successfully.')