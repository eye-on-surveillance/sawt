"""Caption downloader module for YouTube videos."""

import os
import re
import yt_dlp
from typing import Dict, List, Optional
from pathlib import Path


def download_captions(
    video_id: str,
    output_dir: str,
    language: str = "en"
) -> Optional[Dict[str, any]]:
    """
    Download YouTube captions for a video.

    Args:
        video_id: YouTube video ID
        output_dir: Directory to save caption files
        language: Language code for captions (default: "en")

    Returns:
        Dictionary with caption data matching JSON schema, or None if unavailable

    Raises:
        Exception: If download fails for reasons other than missing captions
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    output_template = os.path.join(output_dir, f"{video_id}.%(ext)s")

    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [language],
        'skip_download': True,
        'subtitlesformat': 'vtt',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # Check if captions are available
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})

            has_subtitles = language in subtitles
            has_auto_captions = language in automatic_captions

            if not has_subtitles and not has_auto_captions:
                return None

            # Download captions
            ydl.download([video_url])

            # Determine caption type
            caption_type = "manual" if has_subtitles else "auto-generated"

            # Find the downloaded VTT file
            vtt_file = os.path.join(output_dir, f"{video_id}.{language}.vtt")

            if not os.path.exists(vtt_file):
                return None

            # Parse VTT file
            timestamps, full_text = parse_vtt(vtt_file)

            return {
                'available': True,
                'type': caption_type,
                'language': language,
                'file_path': vtt_file,
                'full_text': full_text,
                'timestamps': timestamps
            }

    except Exception as e:
        # If it's just missing captions, return None
        if "No subtitles" in str(e) or "no caption" in str(e).lower():
            return None
        raise Exception(f"Error downloading captions for {video_id}: {e}")


def parse_vtt(vtt_file: str) -> tuple[List[Dict[str, any]], str]:
    """
    Parse VTT caption file to extract timestamps and text.

    Args:
        vtt_file: Path to VTT file

    Returns:
        Tuple of (timestamps list, full text)
    """
    timestamps = []
    full_text_parts = []

    with open(vtt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into blocks
    blocks = re.split(r'\n\n+', content)

    for block in blocks:
        lines = block.strip().split('\n')

        # Look for timestamp line (format: 00:00:00.000 --> 00:00:05.000)
        timestamp_line = None
        text_lines = []

        for line in lines:
            if '-->' in line:
                timestamp_line = line
            elif line and not line.startswith('WEBVTT') and not line.isdigit():
                # Remove VTT formatting tags
                clean_line = re.sub(r'<[^>]+>', '', line)
                if clean_line.strip():
                    text_lines.append(clean_line.strip())

        if timestamp_line and text_lines:
            # Parse timestamps
            match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})', timestamp_line)
            if match:
                start_time = vtt_time_to_seconds(match.group(1))
                end_time = vtt_time_to_seconds(match.group(2))
                text = ' '.join(text_lines)

                timestamps.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })

                full_text_parts.append(text)

    full_text = ' '.join(full_text_parts)

    return timestamps, full_text


def vtt_time_to_seconds(time_str: str) -> float:
    """
    Convert VTT timestamp to seconds.

    Args:
        time_str: Time string in format HH:MM:SS.mmm

    Returns:
        Time in seconds as float
    """
    # Format: 00:00:05.200
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])

    return hours * 3600 + minutes * 60 + seconds


if __name__ == "__main__":
    # Test caption downloading
    import sys

    if len(sys.argv) > 1:
        test_video_id = sys.argv[1]
    else:
        print("Usage: python caption_downloader.py VIDEO_ID")
        sys.exit(1)

    print(f"Downloading captions for video {test_video_id}...")

    result = download_captions(test_video_id, "../data/raw/captions")

    if result:
        print(f"Success! Type: {result['type']}")
        print(f"Timestamps: {len(result['timestamps'])}")
        print(f"First 200 chars: {result['full_text'][:200]}...")
    else:
        print("No captions available for this video")
