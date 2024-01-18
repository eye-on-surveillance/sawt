from transformers import pipeline

class TranscriptionGenerator:
    def __init__(self, model_size, model_device, model_chunk_length, model_batch_size):
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

    def transcribe(self, audio_path):
        transcript = self.pipe(audio_path)
        return transcript
    
    def export_transcript(self, transcript, save_loc):
        with open(save_loc, 'w') as f:
            json.dump(transcript, f)
        print(f'Transcript saved successfully at {save_loc}')
        
