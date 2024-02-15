import os
import yaml
import argparse
import face_recognition
import pandas as pd
from pydub import AudioSegment
from pytube import YouTube
from transformers import pipeline
import torch
from moviepy.editor import VideoFileClip

from pydub import AudioSegment

import numpy as np
import librosa
import soundfile as sf


from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
from pydub import silence
from scipy.signal import butter, lfilter


def load_config(config_file):
    try:
        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)
        return config
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing config file: {e}")
        return None


def process_segment_with_whisper(segment_path, pipe, model_batch_size):
    transcript = pipe(
        segment_path, batch_size=model_batch_size, return_timestamps=True
    )["chunks"]
    print(f"TRANSCRIPT: {transcript}")

    processed_transcript = []
    for chunk in transcript:
        start, end = chunk["timestamp"]
        processed_transcript.append(
            {
                "start": start,
                "end": end,
                "text": chunk["text"],
            }
        )
    return processed_transcript


def download_youtube_audio(url, save_path):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=save_path)
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp3"
        os.rename(out_file, new_file)
        return new_file
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None


def recognize_faces(frames, face_encodings):
    recognized_faces = {}
    for timestamp, frame in frames.items():
        face_locations = face_recognition.face_locations(frame, model="cnn")
        face_encs = face_recognition.face_encodings(frame, face_locations)
        for face_enc in face_encs:
            matches = face_recognition.compare_faces(
                list(face_encodings.values()), face_enc
            )
            if True in matches:
                first_match_index = matches.index(True)
                name = list(face_encodings.keys())[first_match_index]
                recognized_faces[timestamp] = name
                print(f"Timestamp (ms): {timestamp}, Recognized face: {name}")
    return recognized_faces


def export_transcript(transcript, save_loc):
    with open(save_loc, "w") as file:
        for segment in transcript:
            print(f"TRANSCRIPT SEGMENT IN EXPORT FUNC: {segment}")
            start, end, text = (
                segment["start"],
                segment["end"],
                segment["text"],
            )

            file.write(f"{start}-{end}: {text}\n")


def get_video_duration(video_path):
    with VideoFileClip(video_path) as video:
        return video.duration * 1000


def split_audio(file_path, start_time_ms, end_time_ms, segment_length_ms, output_dir):
    audio = AudioSegment.from_file(file_path)
    audio_segment = audio[start_time_ms:end_time_ms]
    segments = []

    for i in range(0, len(audio_segment), segment_length_ms):
        segment = audio_segment[i : i + segment_length_ms]
        segment_name = f"segment_{i // segment_length_ms}.mp3"
        segment_file = os.path.join(output_dir, segment_name)
        segment.export(segment_file, format="mp3")
        segments.append(segment_file)

    return segments


def preprocess_and_extract_audio(
    video_path, output_audio_path, target_sample_rate=16000
):
    with VideoFileClip(video_path) as video:
        audio = video.audio
        temp_audio_path = "temp_audio.wav"
        audio.write_audiofile(
            temp_audio_path, codec="pcm_s16le"
        ) 

    y, sr = librosa.load(temp_audio_path, sr=target_sample_rate)

    sf.write(output_audio_path, y, target_sample_rate)

    os.remove(temp_audio_path)


def apply_dynamic_range_compression(audio_path):
    audio = AudioSegment.from_file(audio_path)
    compressed_audio = compress_dynamic_range(audio)
    normalized_audio = normalize(compressed_audio)
    compressed_audio_path = "compressed_" + audio_path
    normalized_audio.export(compressed_audio_path, format="mp3")
    return compressed_audio_path


def remove_silence(audio_path, silence_thresh=-40, min_silence_len=1000):
    audio = AudioSegment.from_file(audio_path)
    non_silent_chunks = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len, 
        silence_thresh=silence_thresh,  
        keep_silence=500, 
    )

    processed_audio = AudioSegment.empty()
    for chunk in non_silent_chunks:
        processed_audio += chunk

    processed_audio_path = "processed_" + os.path.basename(audio_path)
    processed_audio.export(processed_audio_path, format="mp3")
    return processed_audio_path


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def bandpass_filter(audio_path, low=300, high=3400, sr=16000):
    y, sr = librosa.load(audio_path, sr=sr)

    y_filtered = butter_bandpass_filter(y, low, high, sr)
    
    filtered_audio_path = "filtered_" + os.path.basename(audio_path)
    sf.write(filtered_audio_path, y_filtered, sr)

    return filtered_audio_path


def change_speed(audio_path, speed=1.0):
    audio = AudioSegment.from_file(audio_path)
    playback_speed_audio = audio.speedup(playback_speed=speed)
    speed_changed_audio_path = "speed_changed_" + audio_path
    playback_speed_audio.export(speed_changed_audio_path, format="mp3")
    return speed_changed_audio_path


def audio_preprocessing_pipeline(audio_segment_path):
    compressed_audio_path = apply_dynamic_range_compression(audio_segment_path)
    
    no_silence_audio_path = remove_silence(compressed_audio_path)

    filtered_audio_path = bandpass_filter(no_silence_audio_path)

    return filtered_audio_path  


def process_segment_with_whisper(segment_path, pipe, model_batch_size):
    transcript = pipe(
        segment_path, batch_size=model_batch_size, return_timestamps=True
    )["chunks"]
    print(f"TRANSCRIPT: {transcript}")

    processed_transcript = []
    for chunk in transcript:
        start, end = chunk["timestamp"]
        processed_transcript.append(
            {
                "start": start,
                "end": end,
                "text": chunk["text"],
            }
        )
    return processed_transcript


def extract_audio_from_mp4(video_file_path, output_audio_path):
    """
    Extracts the audio from an MP4 file and saves it as an MP3 file.
    """
    with VideoFileClip(video_file_path) as video:
        audio = video.audio
        audio.write_audiofile(output_audio_path, codec="mp3")
    return output_audio_path


def main():
    parser = argparse.ArgumentParser(
        description="Read configuration from transcribe_config YAML file"
    )
    parser.add_argument("config_file", help="Path to YAML config file")

    args = parser.parse_args()
    config_file = args.config_file
    config = load_config(config_file)

    if config:
        model_size = config["model"]["size"]
        model_device = "cuda" if torch.cuda.is_available() else "mps"
        model_chunk_length = int(config["model"]["chunk_length"])
        model_batch_size = int(config["model"]["batch_size"])

        video_path = "input/Regular Council Mtg 1-4-2024.mp4"
        audio_output_path = "output_audio/test_audio.mp3"
        if not os.path.exists(audio_output_path):
            audio_path = extract_audio_from_mp4(video_path, audio_output_path)
        else:
            print(f"Audio file already exists at {audio_output_path}")
            audio_path = audio_output_path

        config["audio"]["path"] = audio_path

        save_loc = config["transcript"]["save_loc"]

        print("Model Size:", model_size)
        print("Model Device:", model_device)
        print("Chunk Length:", model_chunk_length)
        print("Batch Size", model_batch_size)
        print("Audio Path:", audio_path)
        print("---------------")

        model_names = {
            "tiny": "openai/whisper-tiny.en",
            "base": "openai/whisper-base.en",
            "small": "openai/whisper-small.en",
            "medium": "openai/whisper-medium.en",
            "large": "openai/whisper-large",
            "large-v2": "openai/whisper-large-v2",
            "large-v3": "openai/whisper-large-v3",
        }

        model = model_names.get(model_size, "openai/whisper-large")

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            chunk_length_s=model_chunk_length,
            device=model_device,
        )

        total_duration_ms = get_video_duration(video_path)
        last_15_minutes_ms = 15 * 60 * 1000
        start_time_ms = max(total_duration_ms - last_15_minutes_ms, 0)
        end_time_ms = total_duration_ms

        audio = AudioSegment.from_file(audio_path)
        last_15_min_audio = audio[start_time_ms:end_time_ms]
        last_15_min_audio_path = os.path.join("output_audio", "last_15_min.mp3")
        last_15_min_audio.export(last_15_min_audio_path, format="mp3")

        preprocessed_audio_path = audio_preprocessing_pipeline(
            last_15_min_audio_path
        ) 

        print(f"Processing audio: {preprocessed_audio_path}")
        full_transcript = process_segment_with_whisper(
            preprocessed_audio_path, pipe, model_batch_size
        )

        export_transcript(full_transcript, save_loc)

        print("Transcription Complete. Saved to", save_loc)


if __name__ == "__main__":
    main()
