"""Video discovery module for YouTube channels."""

import yt_dlp
from datetime import datetime
from typing import List, Dict, Optional


def get_channel_videos(
    channel_url: str,
    date_filter: str = "now-1month"
) -> List[Dict[str, any]]:
    """
    Fetch videos from a YouTube channel filtered by date.

    Args:
        channel_url: URL of the YouTube channel
        date_filter: Date filter string (e.g., "now-1month", "now-1week")

    Returns:
        List of video metadata dictionaries

    Raises:
        Exception: If channel cannot be accessed or network error occurs
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'daterange': yt_dlp.DateRange(date_filter),
        'ignoreerrors': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android']
            }
        }
    }

    videos = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract channel info
            result = ydl.extract_info(channel_url, download=False)

            if result is None:
                raise Exception(f"Failed to access channel: {channel_url}")

            # Get entries (videos)
            entries = result.get('entries', [])

            for entry in entries:
                if entry is None:
                    continue

                # Get video metadata from flat extraction (no second fetch needed)
                video_id = entry.get('id')
                if not video_id:
                    continue

                # Format upload date from YYYYMMDD to YYYY-MM-DD
                upload_date = entry.get('upload_date', '')
                if upload_date and len(upload_date) == 8:
                    upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"

                video_data = {
                    'video_id': video_id,
                    'title': entry.get('title', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'upload_date': upload_date,
                    'duration_seconds': entry.get('duration', 0),
                    'channel': entry.get('channel', result.get('channel', ''))
                }

                videos.append(video_data)

    except Exception as e:
        raise Exception(f"Error accessing channel {channel_url}: {e}")

    return videos


def format_upload_date(date_str: str) -> str:
    """
    Format YYYYMMDD to YYYY-MM-DD.

    Args:
        date_str: Date string in YYYYMMDD format

    Returns:
        Date string in YYYY-MM-DD format
    """
    if len(date_str) == 8:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    return date_str


if __name__ == "__main__":
    # Test video discovery
    channel = "https://www.youtube.com/@NOLACityCouncil"
    print(f"Fetching videos from {channel}...")

    try:
        videos = get_channel_videos(channel, "now-1month")
        print(f"Found {len(videos)} videos")

        if videos:
            print("\nFirst video:")
            print(f"  Title: {videos[0]['title']}")
            print(f"  ID: {videos[0]['video_id']}")
            print(f"  Duration: {videos[0]['duration_seconds']}s")

    except Exception as e:
        print(f"Error: {e}")
