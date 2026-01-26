"""Whisper transcription module using HuggingFace transformers."""

import os
# Fix for macOS threading issue with transformers
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

import time
import torch
from transformers import pipeline
from typing import Dict, List
import soundfile as sf

# Force single-threaded execution for macOS compatibility
torch.set_num_threads(1)
torch.set_num_interop_threads(1)


def transcribe_audio(
    audio_file: str,
    model_name: str = "openai/whisper-large-v3-turbo",
    device: str = "cuda",
    torch_dtype: str = "float16",
    language: str = "en",
    batch_size: int = 8,
    chunk_length_s: int = 30,
    return_timestamps: bool = True
) -> Dict[str, any]:
    """
    Transcribe audio file using Whisper model.

    Args:
        audio_file: Path to audio file
        model_name: HuggingFace model name
        device: Device to use ("cuda" or "cpu")
        torch_dtype: Torch dtype ("float16" or "float32")
        language: Language code
        batch_size: Batch size for processing
        chunk_length_s: Chunk length in seconds
        return_timestamps: Whether to return timestamps

    Returns:
        Dictionary with transcription data matching JSON schema

    Raises:
        Exception: If transcription fails
    """
    print(f"Initializing Whisper model: {model_name}")

    # Check device availability
    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"
        torch_dtype = "float32"

    # Set torch dtype
    if torch_dtype == "float16":
        dtype = torch.float16
    else:
        dtype = torch.float32

    try:
        # Initialize pipeline
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            torch_dtype=dtype,
            device=device,
            model_kwargs={"attn_implementation": "sdpa"} if device == "cuda" else {}
        )

        print(f"Loading audio file: {audio_file}")
        start_time = time.time()

        # Load audio
        audio_data, sample_rate = sf.read(audio_file)

        # Get duration
        duration_seconds = len(audio_data) / sample_rate

        print(f"Transcribing audio ({duration_seconds:.2f}s)...")

        # Transcribe
        result = pipe(
            audio_file,
            chunk_length_s=chunk_length_s,
            batch_size=batch_size,
            return_timestamps=return_timestamps,
            generate_kwargs={"language": language}
        )

        processing_time = time.time() - start_time

        print(f"Transcription completed in {processing_time:.2f}s")

        # Format output to match JSON schema
        chunks = []
        if return_timestamps and "chunks" in result:
            for chunk in result["chunks"]:
                chunks.append({
                    "timestamp": chunk["timestamp"],
                    "text": chunk["text"].strip()
                })

        return {
            "model": model_name,
            "language": language,
            "duration_seconds": duration_seconds,
            "processing_time_seconds": processing_time,
            "audio_file_path": audio_file,
            "full_text": result["text"].strip(),
            "chunks": chunks
        }

    except Exception as e:
        raise Exception(f"Error transcribing {audio_file}: {e}")


def initialize_model(
    model_name: str = "openai/whisper-large-v3-turbo",
    device: str = "cuda"
) -> pipeline:
    """
    Pre-initialize Whisper model for reuse.

    Args:
        model_name: HuggingFace model name
        device: Device to use

    Returns:
        Initialized pipeline
    """
    # Check device availability
    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"
        dtype = torch.float32
    else:
        dtype = torch.float16 if device == "cuda" else torch.float32

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model_name,
        torch_dtype=dtype,
        device=device,
        model_kwargs={"attn_implementation": "sdpa"} if device == "cuda" else {}
    )

    return pipe


def transcribe_with_pipeline(
    audio_file: str,
    pipe: pipeline,
    language: str = "en",
    batch_size: int = 8,
    chunk_length_s: int = 30
) -> Dict[str, any]:
    """
    Transcribe using pre-initialized pipeline.

    Args:
        audio_file: Path to audio file
        pipe: Pre-initialized pipeline
        language: Language code
        batch_size: Batch size
        chunk_length_s: Chunk length in seconds

    Returns:
        Dictionary with transcription data
    """
    start_time = time.time()

    # Load audio for duration
    audio_data, sample_rate = sf.read(audio_file)
    duration_seconds = len(audio_data) / sample_rate

    # Transcribe
    result = pipe(
        audio_file,
        chunk_length_s=chunk_length_s,
        batch_size=batch_size,
        return_timestamps=True,
        generate_kwargs={"language": language}
    )

    processing_time = time.time() - start_time

    # Format chunks
    chunks = []
    if "chunks" in result:
        for chunk in result["chunks"]:
            chunks.append({
                "timestamp": chunk["timestamp"],
                "text": chunk["text"].strip()
            })

    return {
        "model": pipe.model.name_or_path,
        "language": language,
        "duration_seconds": duration_seconds,
        "processing_time_seconds": processing_time,
        "audio_file_path": audio_file,
        "full_text": result["text"].strip(),
        "chunks": chunks
    }


if __name__ == "__main__":
    # Test transcription
    import sys

    if len(sys.argv) > 1:
        test_audio = sys.argv[1]
    else:
        print("Usage: python whisper_transcriber.py AUDIO_FILE")
        sys.exit(1)

    print(f"Testing Whisper transcription on: {test_audio}")

    try:
        result = transcribe_audio(test_audio)
        print(f"\nTranscription successful!")
        print(f"Model: {result['model']}")
        print(f"Duration: {result['duration_seconds']:.2f}s")
        print(f"Processing time: {result['processing_time_seconds']:.2f}s")
        print(f"Chunks: {len(result['chunks'])}")
        print(f"\nFirst 200 chars:")
        print(result['full_text'][:200])

    except Exception as e:
        print(f"Error: {e}")
