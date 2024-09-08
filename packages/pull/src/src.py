import json
from youtube_transcript_api import YouTubeTranscriptApi

video_data = [
    ['https://www.youtube.com/watch?v=j3wYgcTct2E', 'City Council Meeting 11/16/2023', '11/16/2023'],
    ['https://www.youtube.com/watch?v=kbkCH8CLCws', 'City Council Meeting 12/1/2023', '12/1/2023'],
    ['https://www.youtube.com/watch?v=HB2HEqcf_rc', 'City Council Meeting 12/14/2023', '12/14/2023'],
    ['https://www.youtube.com/watch?v=_xvqfFhZEaw', 'City Council Meeting 12/14/2023', '12/14/2023'],
    ['https://www.youtube.com/watch?v=no7WCBwIXTk', 'City Council Meeting 1/4/2024', '1/4/2024'],
    ['https://www.youtube.com/watch?v=XykfGH6ywHk', 'City Council Meeting 1/18/2024', '1/18/2024'],
    ['https://www.youtube.com/watch?v=mDpOsEnGH8A', 'City Council Meeting 1/18/2024 pt2', '1/18/2024 pt2'],
    ['https://www.youtube.com/watch?v=BPVdYzbyaG0', 'City Council Meeting 1/18/2024', '1/18/2024'],
    ['https://www.youtube.com/watch?v=cuMo0btkCc0', 'City Council Meeting 2/1/2024', '2/1/2024'],
    ['https://www.youtube.com/watch?v=7RDZI3B6RcY', 'City Council Meeting 2/22/2024', '2/22/2024'],
    ['https://www.youtube.com/watch?v=favibGZ_ksY', 'City Council Meeting 3/7/2024', '3/7/2024'],
    ['https://www.youtube.com/watch?v=kDUWcHJHE-U', 'City Council Meeting 3/21/2024', '3/21/2024'],
    ['https://www.youtube.com/watch?v=5ZOofdp8XH8', 'City Council Meeting 4/4/2024', '4/4/2024'],
    ['https://www.youtube.com/watch?v=FF8FfduEA1Q', 'City Council Meeting 4/18/2024', '4/18/2024'],
    ['https://www.youtube.com/watch?v=yeJuIsl8od0', 'City Council Meeting 5/2/2024', '5/2/2024'],
    ['https://www.youtube.com/watch?v=Q2ocfAFWgd0', 'City Council Meeting 6/6/2024', '6/6/2024'],
]

all_segments = []

for video_url, video_title, publish_date in video_data:
    video_id = video_url.split('v=')[1].split('&')[0]
    
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en']).fetch()
    except Exception as e:
        print(f'Error retrieving transcript for video {video_id}: {str(e)}')
        continue
    
    segments = []
    current_segment = ''
    start_time = None
    
    for entry in transcript:
        start = entry['start']
        duration = entry['duration']
        text = entry['text']
        
        if start_time is None:
            start_time = start
        
        if start - start_time >= 30:
            end_time = start
            timestamp = f"{int(start_time//60)}:{int(start_time%60):02d}-{int(end_time//60)}:{int(end_time%60):02d}"
            segments.append({
                'timestamp': timestamp,
                'page_content': current_segment.strip(),
                'url': video_url,
                'title': video_title,
                'publish_date': publish_date
            })
            current_segment = ''
            start_time = start
        
        current_segment += ' ' + text.strip()
    
    end_time = start + duration
    timestamp = f"{int(start_time//60)}:{int(start_time%60):02d}-{int(end_time//60)}:{int(end_time%60):02d}"
    segments.append({
        'timestamp': timestamp,
        'page_content': current_segment.strip(),
        'url': video_url,
        'title': video_title,
        'publish_date': publish_date
    })
    
    all_segments.extend(segments)

output = {'messages': all_segments}
with open('../../backend/src/json_fc_directory/fc_transcript_11-2024_5-2024.json', 'w') as f:
    json.dump(output, f, indent=2)

print('All transcript segments saved to afc_transcript_11-2024_5-2024.json')