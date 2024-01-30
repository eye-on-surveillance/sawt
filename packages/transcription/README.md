**Transcription Management Folder**

***yt-transcribe***
In yttranscriptions.py, the class YouTubeTranscriptions can be used to interact with YouTube audio and video files, as well as native transcripts. This requires YOUTUBE_API_KEY, CLIENT_ID, CLIENT_SECRET, and GOOGLE_APPLICATION_CREDENTIALS per YouTube API documentation. 

Methods:
    - get_latest_videos(channel_id, max_results = 5):
    Get the "max_results" number of videos from a youtube channel with ID "channel_id". Returns a list of video IDs for the latest videos.
    - download_transcripts(video_ids):
    For each ID in the array "video_ids", try to download the native YouTube transcript via the YouTube API. Saved as .json.
    - download_audio(video_ids, audio_path):
    For each ID in the array "video_ids", download the audio stream to the specified output path. Saved as .mp4.

***whisper***
In transcribe.py, the class TranscriptionGenerator can be used to locally generate transcripts form audio files, for use when premade transcript not available, Powered by OpenAI Whisper model.

Methods:
    - transcribe(audio_path):
    Given the audio file at "audio_path", use Whisper model of specified size via class pipeline object to generate a audio transcript locally. 
    - export_transcript(transcript, save_loc):
    Given the transcript object "transcript", save it to save location "save_loc". Saved as .json.