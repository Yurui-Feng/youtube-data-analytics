from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from airflow.models import Variable
import os
import json
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description='Fetch YouTube Channel Videos')
parser.add_argument('--channel_id', required=True, help='YouTube Channel ID')
args = parser.parse_args()

# api_key = os.getenv('GOOGLE_API_KEY')
api_key = Variable.get('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("The GOOGLE_API_KEY environment variable is not set.")

channel_id = args.channel_id

try:
    youtube = build('youtube', 'v3', developerKey=api_key)

    def get_channel_videos(channel_id):
        videos = []
        next_page_token = None

        while True:
            request = youtube.search().list(
                part='id,snippet',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token,
                type='video'
            )
            response = request.execute()

            for item in response['items']:
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                video_description = item['snippet']['description']
                publish_time = item['snippet']['publishedAt']
                video_request = youtube.videos().list(
                    part='statistics',
                    id=video_id
                )
                video_response = video_request.execute()
                video_stats = video_response['items'][0]['statistics']

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

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return videos

    videos = get_channel_videos(channel_id)

    # Save the video data as JSON
    with open('video_data.json', 'w') as file:
        json.dump(videos, file, indent=4)

except HttpError as error:
    # Prints details of the HTTPError.
    print(f'An HTTP error occurred: {error.resp.status} {error.content}')
    exit(1)
