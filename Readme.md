# YouTube Analytics

This repository contains scripts for collecting YouTube video data and uploading it to an S3 bucket. 

## Setup

1. Set up a virtual environment using the `requirements.txt` file:

    ```bash
    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    ```

2. Run the `video_data_collector.py` script to collect video data. This script requires a specific channel ID as input and will generate a file called `video_data.json`:

    ```bash
    $ python video_data_collector.py --channel-id <channel-id>
    ```

3. Before running the `upload_to_s3.py` script, make sure to configure your AWS credentials and provide your own S3 bucket name in the script:

    ```python
    # Configure AWS credentials
    aws_access_key_id = 'your-access-key-id'
    aws_secret_access_key = 'your-secret-access-key'
    aws_region = 'your-aws-region'

    # Set S3 bucket name
    s3_bucket_name = 'your-s3-bucket-name'
    ```

4. Run the `upload_to_s3.py` script to upload the `video_data.json` file to the configured S3 bucket:

    ```bash
    $ python upload_to_s3.py
    ```

