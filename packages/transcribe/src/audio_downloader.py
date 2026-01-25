"""Audio downloader module for YouTube videos."""

import os
import yt_dlp
from pathlib import Path
from typing import Optional


def download_audio(
    video_id: str,
    output_dir: str,
    format: str = "mp3"
) -> str:
    """
    Download audio from a YouTube video.

    Args:
        video_id: YouTube video ID
        output_dir: Directory to save audio files
        format: Audio format (default: "mp3")

    Returns:
        Path to downloaded audio file

    Raises:
        Exception: If download fails
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    output_file = os.path.join(output_dir, f"{video_id}.{format}")

    # If file already exists, return it
    if os.path.exists(output_file):
        print(f"Audio file already exists: {output_file}")
        return output_file

    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': format,
        'preferredquality': '192',
    }],
    'outtmpl': os.path.join(output_dir, f"{video_id}.%(ext)s"),
    'quiet': False,
    'no_warnings': False,
    'progress_hooks': [progress_hook],
    # Add these headers
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
    },
}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading audio for video {video_id}...")
            ydl.download([video_url])

        if not os.path.exists(output_file):
            raise Exception(f"Audio file was not created: {output_file}")

        print(f"Audio downloaded successfully: {output_file}")
        return output_file

    except Exception as e:
        raise Exception(f"Error downloading audio for {video_id}: {e}")


def progress_hook(d):
    """
    Progress hook for yt-dlp to display download progress.

    Args:
        d: Progress dictionary from yt-dlp
    """
    if d['status'] == 'downloading':
        # Display progress
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}", end='', flush=True)
    elif d['status'] == 'finished':
        print(f"\nDownload finished, now converting...")


def get_audio_duration(audio_file: str) -> Optional[float]:
    """
    Get duration of audio file in seconds.

    Args:
        audio_file: Path to audio file

    Returns:
        Duration in seconds, or None if cannot be determined
    """
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return float(result.stdout.strip())
    except Exception:
        pass
    return None


if __name__ == "__main__":
    # Test audio downloading
    import sys

    if len(sys.argv) > 1:
        test_video_id = sys.argv[1]
    else:
        print("Usage: python audio_downloader.py VIDEO_ID")
        sys.exit(1)

    print(f"Downloading audio for video {test_video_id}...")

    try:
        audio_path = download_audio(test_video_id, "../data/raw/audio")
        print(f"Audio saved to: {audio_path}")

        duration = get_audio_duration(audio_path)
        if duration:
            print(f"Duration: {duration:.2f} seconds")

    except Exception as e:
        print(f"Error: {e}")
