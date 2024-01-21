from transformers import pipeline
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

class TranscriptionGenerator:
    def __init__(self, model_size = 'tiny', model_device = 'cpu', model_chunk_length = 30, model_batch_size = 12):
        self.model_size = model_size
        self.model_device = model_device
        self.model_chunk_length = model_chunk_length
        self.model_batch_size = model_batch_size
        
        self.model_names = {"tiny":"openai/whisper-tiny.en",
                            "base":"openai/whisper-base.en",
                            "small":"openai/whisper-small.en",
                            "medium":"openai/whisper-medium.en",
                            "large":"openai/whisper-large",
                            "large_v2":"openai/whisper-large-v2"}
        
        self.model = self.model_names[model_size]
        
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model = self.model,
            chunk_length_s = self.model_chunk_length,
            device = self.model_device,
            return_timestamps = True
        )

    def convert_video_to_audio(input_path, output_path, audio_format="mp3"):
    # Load video clip
        video_clip = VideoFileClip(input_path)
    
        # Extract audio from the video
        audio_clip = video_clip.audio
    
        # Save audio to the specified output path and format
        audio_clip.write_audiofile(output_path, codec = 'mp3')
    
        # Close the video and audio clips
        video_clip.close()
        audio_clip.close()

    
