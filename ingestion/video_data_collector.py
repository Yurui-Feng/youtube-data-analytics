from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)

api_key = os.getenv('GOOGLE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)

channel_id = "UCwdogH5kbb9wGy2Amvw6KeQ"

def get_channel_videos(channel_id):
    videos = []
    next_page_token = None

    while True:
        # Retrieve the list of videos in the channel
        request = youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token,
            type='video'
        )
        response = request.execute()

        # Extract video details
        for item in response['items']:
            video_id = item['id']['videoId']
            video_title = item['snippet']['title']
            video_description = item['snippet']['description']
            publish_time = item['snippet']['publishedAt']

            # Retrieve additional video statistics
            video_request = youtube.videos().list(
                part='statistics',
                id=video_id
            )
            video_response = video_request.execute()
            video_stats = video_response['items'][0]['statistics']

            # Create a dictionary with video details
            video_data = {
                'video_id': video_id,
                'title': video_title,
                'description': video_description,
                'publish_time': publish_time,
                'view_count': video_stats.get('viewCount', 0),
                'like_count': video_stats.get('likeCount', 0),
                'comment_count': video_stats.get('commentCount', 0)
            }
            videos.append(video_data)

        # Check if there are more pages of videos
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos


videos = get_channel_videos(channel_id)

# Save the video data as JSON
with open('video_data.json', 'w') as file:
    json.dump(videos, file, indent=4)