"""Data storage module for saving transcription results."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, List


def save_transcription(
    video_id: str,
    video_metadata: Dict[str, any],
    youtube_captions: Optional[Dict[str, any]],
    whisper_transcription: Dict[str, any],
    output_dir: str,
    pipeline_version: str = "1.0"
) -> str:
    """
    Save combined transcription data to JSON file.

    Args:
        video_id: YouTube video ID
        video_metadata: Video metadata dictionary
        youtube_captions: Caption data (or None if unavailable)
        whisper_transcription: Whisper transcription data
        output_dir: Directory to save JSON files
        pipeline_version: Version string for pipeline

    Returns:
        Path to saved JSON file

    Raises:
        Exception: If save fails
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Build the complete JSON structure
    output_data = {
        "video_metadata": video_metadata,
        "youtube_captions": youtube_captions if youtube_captions else {
            "available": False,
            "type": None,
            "language": None,
            "file_path": None,
            "full_text": None,
            "timestamps": []
        },
        "whisper_transcription": whisper_transcription,
        "processing_metadata": {
            "pipeline_version": pipeline_version,
            "processed_date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "status": "completed",
            "errors": []
        }
    }

    # Save to file
    output_file = os.path.join(output_dir, f"{video_id}.json")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Saved transcription to: {output_file}")
        return output_file

    except Exception as e:
        raise Exception(f"Error saving transcription for {video_id}: {e}")


def save_with_errors(
    video_id: str,
    video_metadata: Dict[str, any],
    errors: List[str],
    output_dir: str,
    pipeline_version: str = "1.0"
) -> str:
    """
    Save partial data when processing fails.

    Args:
        video_id: YouTube video ID
        video_metadata: Video metadata dictionary
        errors: List of error messages
        output_dir: Directory to save JSON files
        pipeline_version: Version string for pipeline

    Returns:
        Path to saved JSON file
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_data = {
        "video_metadata": video_metadata,
        "youtube_captions": {
            "available": False,
            "type": None,
            "language": None,
            "file_path": None,
            "full_text": None,
            "timestamps": []
        },
        "whisper_transcription": {
            "model": None,
            "language": None,
            "duration_seconds": 0,
            "processing_time_seconds": 0,
            "audio_file_path": None,
            "full_text": None,
            "chunks": []
        },
        "processing_metadata": {
            "pipeline_version": pipeline_version,
            "processed_date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "status": "failed",
            "errors": errors
        }
    }

    output_file = os.path.join(output_dir, f"{video_id}.json")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return output_file


def create_manifest(
    output_dir: str,
    metadata_dir: str,
    processed_videos: List[Dict[str, any]]
) -> str:
    """
    Create manifest file listing all processed videos.

    Args:
        output_dir: Directory containing JSON files
        metadata_dir: Directory to save manifest
        processed_videos: List of processed video info

    Returns:
        Path to manifest file
    """
    Path(metadata_dir).mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_date": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "total_videos": len(processed_videos),
        "videos": processed_videos
    }

    manifest_file = os.path.join(metadata_dir, "manifest.json")

    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Manifest saved to: {manifest_file}")
    return manifest_file


def load_transcription(json_file: str) -> Dict[str, any]:
    """
    Load transcription data from JSON file.

    Args:
        json_file: Path to JSON file

    Returns:
        Dictionary with transcription data

    Raises:
        Exception: If load fails
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise Exception(f"Error loading {json_file}: {e}")


if __name__ == "__main__":
    # Test data storage
    test_metadata = {
        "video_id": "TEST_123",
        "title": "Test Video",
        "url": "https://youtube.com/watch?v=TEST_123",
        "upload_date": "2026-01-25",
        "duration_seconds": 100,
        "channel": "Test Channel"
    }

    test_captions = {
        "available": True,
        "type": "auto-generated",
        "language": "en",
        "file_path": "test.vtt",
        "full_text": "Test caption text",
        "timestamps": [{"start": 0.0, "end": 5.0, "text": "Test"}]
    }

    test_whisper = {
        "model": "openai/whisper-large-v3-turbo",
        "language": "en",
        "duration_seconds": 100,
        "processing_time_seconds": 10,
        "audio_file_path": "test.mp3",
        "full_text": "Test transcription",
        "chunks": [{"timestamp": [0.0, 5.0], "text": "Test"}]
    }

    output_file = save_transcription(
        "TEST_123",
        test_metadata,
        test_captions,
        test_whisper,
        "../data/output/structured"
    )

    print(f"Test file created: {output_file}")

    # Verify
    loaded = load_transcription(output_file)
    print(f"Loaded keys: {list(loaded.keys())}")
