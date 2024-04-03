import boto3
import json
import os
import argparse
from botocore.exceptions import NoCredentialsError, ClientError
from airflow.models import Variable

# Set up argument parsing
parser = argparse.ArgumentParser(description='Upload data to S3 with dynamic folder naming based on channel name')
parser.add_argument('--channel_name', required=True, help='Name of the YouTube Channel')
args = parser.parse_args()

# Verify AWS credentials are set
# if not os.getenv('AWS_ACCESS_KEY_ID') or not os.getenv('AWS_SECRET_ACCESS_KEY'):
#     raise ValueError("AWS credentials are not set in environment variables.")



try:
    s3 = boto3.client('s3',
                      aws_access_key_id=Variable.get('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=Variable.get('AWS_SECRET_ACCESS_KEY'))

    # Default parameters with dynamic S3 key based on channel name
    bucket_name = 'video-analytics-goalcast'
    file_name = 'video_data.json'
    s3_file_key = f'{args.channel_name}/raw/{file_name}'

    # Attempt to open and read the file
    with open(file_name, 'r') as file:
        data = json.load(file)

    upload_data = json.dumps(data, indent=4)

    # Attempt to upload the file
    s3.put_object(Bucket=bucket_name, Key=s3_file_key, Body=upload_data)
    print(f'{file_name} has been uploaded to {bucket_name}/{s3_file_key}')

except FileNotFoundError:
    print(f"Error: The file {file_name} was not found.")
    exit(1)
except NoCredentialsError:
    print("Error: AWS credentials not found.")
    exit(1)
except ClientError as e:
    print(f"An error occurred: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)
