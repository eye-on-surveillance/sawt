# HF Whisper Transcript App
Application of [OpenAI Whisper-V2](https://huggingface.co/openai/whisper-large-v2) for audio file transcription.


## To Run
Configure [README.md]('README.md')
```yml
model:
  #model size
  #tiny, base, small, medium, large, large_v2
  size: "tiny" 
  # device for pytorch processing
  device: "cpu"
  # chunk length for audio processing
  chunk_length: "10"
  # batch size
  batch_size: 1
audio:
  # path to audio file to process
  path: "audio/trial_meeting.mp3"
transcript:
  # location to save transcript
  save_loc: "transcripts/trial_meeting_transcript.txt" 
```
Execute from CL:
```bash
python transcribe.py transcribe_config.yml
```