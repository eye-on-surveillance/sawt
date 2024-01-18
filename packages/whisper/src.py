import os
import yaml
import argparse
import face_recognition
import cv2
import pandas as pd
from pydub import AudioSegment
from pytube import YouTube

from transformers import pipeline
from pyannote.audio import Pipeline
import torch
from moviepy.editor import VideoFileClip

def load_config(config_file):
    try:
        with open(config_file, 'r') as stream:
            config = yaml.safe_load(stream)
        return config
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing config file: {e}")
        return None

def load_face_labels(csv_file):
    df = pd.read_csv(csv_file)

    df.loc[:, "label"] = df.label.str.lower()
    df.loc[:, "filepath"] = df.filepath.str.lower()
    base_path = os.path.join(os.getcwd(), 'training_data')  # Base path for images
    adjusted_filepaths = [os.path.join(base_path, path) for path in df['filepath']]
    return dict(zip(adjusted_filepaths, df['label']))

def preprocess_audio_for_diarization(file_path):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    preprocessed_path = file_path.replace('.mp3', '_preprocessed.wav')
    audio.export(preprocessed_path, format="wav")
    return preprocessed_path

def perform_diarization(file_path, access_token):
    diarization_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=access_token)
    diarization = diarization_pipeline(file_path)
    return diarization

def split_audio(file_path, start_time_ms, end_time_ms, segment_length_ms, output_dir):
    audio = AudioSegment.from_file(file_path)
    audio_segment = audio[start_time_ms:end_time_ms]  
    segments = []

    for i in range(0, len(audio_segment), segment_length_ms):
        segment = audio_segment[i:i + segment_length_ms]
        segment_name = f"segment_{i // segment_length_ms}.mp3"
        segment_file = os.path.join(output_dir, segment_name)
        segment.export(segment_file, format="mp3")
        segments.append(segment_file)

    return segments

def process_segment_with_whisper_and_diarization(segment_path, diarization_results, pipe, model_batch_size):
    transcript = pipe(segment_path, batch_size=model_batch_size, return_timestamps=True)["chunks"]
    print(f"TRANSCRIPT: {transcript}")

    diarized_transcript = []
    for chunk in transcript:
        start, end = chunk['timestamp']  
        speaker_label = get_speaker_label(diarization_results, start, end)
        diarized_transcript.append({
            'start': start,
            'end': end,
            'speaker': speaker_label,
            'text': chunk['text']
        })
    return diarized_transcript

def get_speaker_label(diarization_results, start, end):
    # Handle None values for start and end
    if start is None or end is None:
        return None

    # Find the speaker with the most overlap with the given time range
    overlap = {}
    for turn, _, speaker in diarization_results.itertracks(yield_label=True):
        if turn.end < start or turn.start > end:
            continue
        overlap[speaker] = overlap.get(speaker, 0) + min(end, turn.end) - max(start, turn.start)
    if overlap:
        return max(overlap, key=overlap.get)
    return None

def download_youtube_audio(url, save_path):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=save_path)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        return new_file
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def encode_faces(face_labels):
    face_encodings = {}
    for filepath, label in face_labels.items():
        image = face_recognition.load_image_file(filepath)
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            print(f"No face detected in image: {filepath}, skipping...")
            continue  
        face_encodings[label] = encodings[0]
    return face_encodings

def extract_frames(video_path, timestamps_ms):
    cap = cv2.VideoCapture(video_path)
    frames = {}

    for timestamp_ms in timestamps_ms:
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        ret, frame = cap.read()
        if ret:
            frames[timestamp_ms] = frame
    cap.release()
    return frames

def recognize_faces(frames, face_encodings):
    recognized_faces = {}
    for timestamp, frame in frames.items():
        face_locations = face_recognition.face_locations(frame, model="cnn")
        face_encs = face_recognition.face_encodings(frame, face_locations)
        for face_enc in face_encs:
            matches = face_recognition.compare_faces(list(face_encodings.values()), face_enc)
            if True in matches:
                first_match_index = matches.index(True)
                name = list(face_encodings.keys())[first_match_index]
                recognized_faces[timestamp] = name
                print(f"Timestamp (ms): {timestamp}, Recognized face: {name}")  # Print statement added
    return recognized_faces

def map_faces_to_speakers(diarized_transcript, recognized_faces, tolerance_ms=1000):
    speaker_mapping = {}
    labelname_to_speaker_mapping = {}

    print("Received Recognized Faces (ms):", recognized_faces)

    for segment_tuple in diarized_transcript:
        segment, speaker = segment_tuple
        segment_start_ms = segment.start * 1000  # Convert to milliseconds
        segment_end_ms = segment.end * 1000  # Convert to milliseconds
        segment_speakers = []

        print(f"\nProcessing Segment: [{segment_start_ms} - {segment_end_ms}], Speaker Label: {speaker}")

        for face_time_ms, name in recognized_faces.items():
            print(f"  Checking Face Time: {face_time_ms}, Name: {name}")

            if (segment_start_ms - tolerance_ms) <= face_time_ms <= (segment_end_ms + tolerance_ms):
                segment_speakers.append(name)
                print(f"    Matching Face Detected - Time (ms): {face_time_ms}, Name: {name}")
        
        recognized_speaker = max(set(segment_speakers), key=segment_speakers.count) if segment_speakers else None
        identified_speaker = recognized_speaker if recognized_speaker else speaker

        # Update the main speaker mapping
        speaker_mapping[(segment_start_ms, segment_end_ms)] = identified_speaker

        # Correctly update labelname_to_speaker_mapping
        if recognized_speaker:
            # Map the original speaker label to the recognized speaker's name
            labelname_to_speaker_mapping[speaker] = recognized_speaker

        print(f"  Finalized Mapping for Segment: {segment_start_ms} - {segment_end_ms}, Speaker: {identified_speaker}")

    return speaker_mapping, labelname_to_speaker_mapping


def export_diarized_transcript_with_names(diarized_transcript, labelname_to_speaker_mapping, save_loc):
    with open(save_loc, 'w') as file:
        for segment in diarized_transcript:
            print(f"DIARIZED SEGMENT IN EXPORT FUNC: {segment}")
            start, end, original_speaker_label, text = segment['start'], segment['end'], segment['speaker'], segment['text']

            # Use the labelname_to_speaker mapping to update the speaker label
            updated_speaker_label = labelname_to_speaker_mapping.get(original_speaker_label, original_speaker_label)

            file.write(f"{start}-{end} {updated_speaker_label}: {text}\n")

def extract_audio_from_mp4(video_file_path, output_audio_path):
    """
    Extracts the audio from an MP4 file and saves it as an MP3 file.
    """
    with VideoFileClip(video_file_path) as video:
        audio = video.audio
        audio.write_audiofile(output_audio_path, codec='mp3')
    return output_audio_path


def main():
    parser = argparse.ArgumentParser(description="Read configuration from transcribe_config YAML file")
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
            "large-v2": "openai/whisper-large-v2"
        }

        model = model_names.get(model_size, "openai/whisper-tiny")  # Default to large if not found

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            chunk_length_s=model_chunk_length,
            device=model_device
        )

        start_time_ms = (1 * 60 * 60 + 10 * 60) * 1000
        end_time_ms = (1 * 60 * 60 + 18 * 60) * 1000

        # Length of each segment (1 minute per segment)
        segment_length_ms = 300000  # 1 minute in milliseconds

        segments = split_audio(audio_path, start_time_ms, end_time_ms, segment_length_ms, 'output_audio')

        access_token = "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"

        full_diarized_transcript = []
        combined_diarization_data = []  
        if segments:
            segment = segments[0] 
            print(f"Processing segment: {segment}")

            preprocessed_segment_path = preprocess_audio_for_diarization(segment)
            diarization = perform_diarization(preprocessed_segment_path, access_token)

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                combined_diarization_data.append((turn, speaker))

            segment_transcript = process_segment_with_whisper_and_diarization(segment, diarization, pipe,
                                                                              model_batch_size)
            full_diarized_transcript.extend(segment_transcript)
            os.remove(segment)

            # Load face labels from CSV and prepare face recognition
            face_labels = load_face_labels("training_data/training_data.csv")
            face_encodings = encode_faces(face_labels)
            video_path = "input/Regular Council Mtg 1-4-2024.mp4"
            
            offset_ms = start_time_ms  # Start time in milliseconds (1 hour 10 minutes into the video)

            # Adjust timestamps for frame extraction
            adjusted_timestamps = []
            for segment in full_diarized_transcript:
                if segment['end'] is None or segment['speaker'] is None:
                    continue

                print("Start ms", segment)
                # Convert start time to milliseconds and add offset
                start_ms = int(segment['start'] * 1000) + offset_ms
                adjusted_timestamps.append(start_ms)

            # Remove duplicates if necessary
            # adjusted_timestamps = sorted(set(adjusted_timestamps))
            print(f"Adjusted timestamps {adjusted_timestamps}")

            # Extract and save frames
            frames = extract_frames(video_path, adjusted_timestamps)
            for timestamp in adjusted_timestamps:
                print("TIMESTAMP FOR FRAME: {timestamp}")
                if timestamp in frames:
                    frame = frames[timestamp]
                    filename = os.path.join("output_frames", f"frame_{timestamp}.jpg")
                    cv2.imwrite(filename, frame)

            # Proceed with face recognition
            recognized_faces = recognize_faces(frames, face_encodings)
            print("Recognized Faces Original", recognized_faces)

            # recognized_faces = {timestamp / 1000.0: name for timestamp, name in recognized_faces.items()}

            recognized_faces_adjusted = {timestamp - offset_ms: name for timestamp, name in recognized_faces.items()}
            print("Adjusted Recognized Faces:", recognized_faces_adjusted)

            print("Combined Diarization Data:", combined_diarization_data)

            # print("FULL Diarization Data:", full_diarized_transcript)

            speaker_mapping, labelname_to_speaker_mapping = map_faces_to_speakers(combined_diarization_data, recognized_faces_adjusted, tolerance_ms=1)

            print("Speaker Mapping:", speaker_mapping)

            print(f"LABEL MAPPING: {labelname_to_speaker_mapping}")

            export_diarized_transcript_with_names(full_diarized_transcript, labelname_to_speaker_mapping, save_loc)

            print("Transcription and Diarization with Speaker Names Complete. Saved to", save_loc)


if __name__ == "__main__":
    main()