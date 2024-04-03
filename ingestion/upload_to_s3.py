import boto3
import json
import os

s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

bucket_name = 'video-analytics-goalcast'

file_name = 'video_data.json'

s3_file_key = 'raw/video_data.json'

with open(file_name, 'r') as file:
    data = json.load(file)

upload_data = json.dumps(data, indent=4)

s3.put_object(Bucket=bucket_name, Key=s3_file_key, Body=upload_data)

print(f'{file_name} has been uploaded to {bucket_name}/{s3_file_key}')