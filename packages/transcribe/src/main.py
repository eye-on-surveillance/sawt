"""Main pipeline orchestrator for YouTube transcription."""

import os
import sys

# Set macOS fork safety environment variable BEFORE any imports
# This prevents mutex lock errors during multiprocessing
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from config import load_config, get_path
from video_discovery import get_channel_videos
from caption_downloader import download_captions
from audio_downloader import download_audio
from whisper_transcriber import transcribe_audio, initialize_model
from data_storage import save_transcription, save_with_errors, create_manifest


def setup_logging(log_dir: str) -> logging.Logger:
    """
    Setup logging configuration.

    Args:
        log_dir: Directory for log files

    Returns:
        Logger instance
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    log_file = Path(log_dir) / "pipeline.log"

    # Create logger
    logger = logging.getLogger("transcription_pipeline")
    logger.setLevel(logging.INFO)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def process_video(
    video_metadata: Dict[str, any],
    config: Dict[str, any],
    logger: logging.Logger,
    whisper_pipe=None
) -> tuple[bool, List[str]]:
    """
    Process a single video: download captions, audio, transcribe, and save.

    Args:
        video_metadata: Video metadata dictionary
        config: Configuration dictionary
        logger: Logger instance
        whisper_pipe: Pre-initialized Whisper pipeline (optional)

    Returns:
        Tuple of (success: bool, errors: List[str])
    """
    video_id = video_metadata['video_id']
    errors = []

    logger.info(f"Processing video: {video_id} - {video_metadata['title']}")

    try:
        # Get paths
        base_dir = Path(__file__).parent
        captions_dir = get_path(config, 'raw_captions', base_dir)
        audio_dir = get_path(config, 'raw_audio', base_dir)
        output_dir = get_path(config, 'output_structured', base_dir)

        # Step 1: Download captions
        logger.info(f"[{video_id}] Downloading captions...")
        try:
            captions = download_captions(
                video_id,
                str(captions_dir),
                language=config['whisper']['language']
            )
            if captions:
                logger.info(f"[{video_id}] Captions downloaded: {captions['type']}")
            else:
                logger.info(f"[{video_id}] No captions available")
        except Exception as e:
            logger.warning(f"[{video_id}] Caption download failed: {e}")
            captions = None
            errors.append(f"Caption download: {str(e)}")

        # Step 2: Download audio
        logger.info(f"[{video_id}] Downloading audio...")
        try:
            audio_path = download_audio(video_id, str(audio_dir))
            logger.info(f"[{video_id}] Audio downloaded: {audio_path}")
        except Exception as e:
            logger.error(f"[{video_id}] Audio download failed: {e}")
            errors.append(f"Audio download: {str(e)}")
            # Save with errors and return
            save_with_errors(video_id, video_metadata, errors, str(output_dir))
            return False, errors

        # Step 3: Transcribe with Whisper
        logger.info(f"[{video_id}] Transcribing with Whisper...")
        try:
            if whisper_pipe:
                from whisper_transcriber import transcribe_with_pipeline
                whisper_result = transcribe_with_pipeline(
                    audio_path,
                    whisper_pipe,
                    language=config['whisper']['language'],
                    batch_size=config['whisper']['batch_size'],
                    chunk_length_s=config['whisper']['chunk_length_s']
                )
            else:
                whisper_result = transcribe_audio(
                    audio_path,
                    model_name=config['whisper']['model'],
                    device=config['whisper']['device'],
                    torch_dtype=config['whisper']['torch_dtype'],
                    language=config['whisper']['language'],
                    batch_size=config['whisper']['batch_size'],
                    chunk_length_s=config['whisper']['chunk_length_s'],
                    return_timestamps=config['whisper']['return_timestamps']
                )

            logger.info(f"[{video_id}] Transcription completed in {whisper_result['processing_time_seconds']:.2f}s")

        except Exception as e:
            logger.error(f"[{video_id}] Transcription failed: {e}")
            errors.append(f"Transcription: {str(e)}")
            # Save with errors and return
            save_with_errors(video_id, video_metadata, errors, str(output_dir))
            return False, errors

        # Step 4: Save combined data
        logger.info(f"[{video_id}] Saving transcription data...")
        try:
            save_transcription(
                video_id,
                video_metadata,
                captions,
                whisper_result,
                str(output_dir)
            )
            logger.info(f"[{video_id}] Processing completed successfully!")
            return True, errors

        except Exception as e:
            logger.error(f"[{video_id}] Save failed: {e}")
            errors.append(f"Save: {str(e)}")
            return False, errors

    except Exception as e:
        logger.error(f"[{video_id}] Unexpected error: {e}")
        errors.append(f"Unexpected: {str(e)}")
        return False, errors


def run_pipeline(config_path: str = "config.yaml", test_mode: bool = False):
    """
    Run the complete transcription pipeline.

    Args:
        config_path: Path to config file
        test_mode: If True, only process the most recent video
    """
    # Load configuration
    config = load_config(config_path)

    # Setup logging
    base_dir = Path(__file__).parent
    log_dir = get_path(config, 'logs', base_dir)
    logger = setup_logging(str(log_dir))

    # Override settings for test mode to run sequentially on CPU
    if test_mode:
        logger.info("Test mode: Forcing CPU device and batch_size=1 for sequential processing")
        config['whisper']['device'] = 'cpu'
        config['whisper']['torch_dtype'] = 'float32'
        config['whisper']['batch_size'] = 1

    logger.info("=" * 80)
    logger.info("YouTube Transcription Pipeline Started")
    logger.info("=" * 80)
    logger.info(f"Channel: {config['youtube']['channel_url']}")
    logger.info(f"Date filter: {config['youtube']['date_filter']}")
    logger.info(f"Whisper model: {config['whisper']['model']}")
    logger.info(f"Batch size: {config['whisper']['batch_size']}")
    logger.info(f"Test mode: {test_mode}")

    # Step 1: Discover videos
    logger.info("\nDiscovering videos from channel...")
    try:
        videos = get_channel_videos(
            config['youtube']['channel_url'],
            config['youtube']['date_filter']
        )
        logger.info(f"Found {len(videos)} videos")

        if len(videos) == 0:
            logger.warning("No videos found!")
            return

        # If test mode, only process a single video (skip first few to avoid rate limits)
        if test_mode:
            videos = videos[4:5]  # Get 5th video to avoid rate-limited recent ones
            logger.info("Test mode: Processing video #5 (skipping most recent to avoid rate limits)")

    except Exception as e:
        logger.error(f"Video discovery failed: {e}")
        return

    # Step 2: Initialize Whisper model (for efficiency)
    logger.info("\nInitializing Whisper model...")
    try:
        whisper_pipe = initialize_model(
            config['whisper']['model'],
            config['whisper']['device']
        )
        logger.info("Whisper model initialized successfully")
    except Exception as e:
        logger.warning(f"Model initialization failed: {e}")
        logger.warning("Will initialize per-video instead")
        whisper_pipe = None

    # Step 3: Process videos
    logger.info(f"\nProcessing {len(videos)} video(s)...\n")

    processed_videos = []
    success_count = 0
    failure_count = 0

    for i, video in enumerate(videos, 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Video {i}/{len(videos)}")
        logger.info(f"{'=' * 60}")

        success, errors = process_video(video, config, logger, whisper_pipe)

        # Track results
        video_result = {
            "video_id": video['video_id'],
            "title": video['title'],
            "success": success,
            "errors": errors
        }
        processed_videos.append(video_result)

        if success:
            success_count += 1
        else:
            failure_count += 1

    # Step 4: Create manifest
    logger.info("\nCreating manifest file...")
    metadata_dir = get_path(config, 'output_metadata', base_dir)
    create_manifest(
        str(get_path(config, 'output_structured', base_dir)),
        str(metadata_dir),
        processed_videos
    )

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("Pipeline Completed")
    logger.info("=" * 80)
    logger.info(f"Total videos: {len(videos)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {failure_count}")

    if failure_count > 0:
        logger.info("\nFailed videos:")
        for video in processed_videos:
            if not video['success']:
                logger.info(f"  - {video['video_id']}: {video['title']}")
                for error in video['errors']:
                    logger.info(f"    Error: {error}")


if __name__ == "__main__":
    # Check for test mode flag
    test_mode = "--test" in sys.argv or "-t" in sys.argv

    if test_mode:
        print("Running in TEST MODE - processing video #5 (skipping recent ones)\n")

    run_pipeline(test_mode=test_mode)
