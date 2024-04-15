# YouTube Analytics

This repository contains scripts for collecting YouTube video data and uploading it to an S3 bucket.

## Setup

1. **Set Up Virtual Environment and Install Dependencies**:
    Create a virtual environment and install necessary Python packages using `requirements.txt`.

    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. **Collect YouTube Video Data**:
    Use `video_data_collector.py` to fetch data from a specific YouTube channel. Provide the channel ID as an argument. This generates a `video_data.json` file.

    ```bash
    python video_data_collector.py --channel-id <channel-id>
    ```

3. **Configure AWS Credentials**:
    Before running the `upload_to_s3.py`, configure your AWS credentials. Replace placeholders with your actual AWS keys and bucket name.

    ```python
    aws_access_key_id = 'your-access-key-id'
    aws_secret_access_key = 'your-secret-access-key'
    aws_region = 'your-aws-region'
    s3_bucket_name = 'your-s3-bucket-name'
    ```

4. **Upload Data to S3**:
    Upload the collected video data to your specified S3 bucket.

    ```bash
    python upload_to_s3.py
    ```

5. **Optional Steps**:
    - Schedule `video_data_collector.py` to run regularly using cron jobs or Airflow to keep data up-to-date.
    - Use AWS Glue for ETL operations and to maintain an up-to-date database via scheduled crawlers and jobs.

6. **AWS Glue and RDS Setup**:
    - Set up AWS Glue to read data from S3 and store it in AWS RDS.
    - Provision an AWS RDS instance using PostgreSQL.
    - Connect to RDS with `psql` and create required tables.

    ```bash
    sudo yum install postgresql15
    psql -h <endpoint-url> -U <username> -d <database-name>
    ```

    ```sql
    CREATE TABLE video_data (
        video_id VARCHAR(255) PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        publish_time TIMESTAMP NOT NULL,
        view_count INT,
        like_count INT,
        comment_count INT,
        engagement_rate FLOAT
    );

    CREATE TABLE top_videos (
        video_id VARCHAR(255) PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        publish_time TIMESTAMP NOT NULL,
        view_count INT,
        like_count INT,
        comment_count INT,
        engagement_rate FLOAT
    );
    ```

7. **Set Up Airflow**:
    Install Airflow and its Amazon provider package to schedule and automate ETL processes.

    ```bash
    pip install "apache-airflow[celery]==2.8.4" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.4/constraints-3.8.txt"
    pip install apache-airflow-providers-amazon
    airflow standalone
    ```

    Access the Airflow webserver at `http://localhost:8080/` and configure environment variables for AWS and Google API keys.

## Debugging

To debug specific tasks within the Airflow pipeline, you can manually test them:

```bash
airflow tasks test youtube_data_pipeline preprocess_data '2023-01-01'
airflow tasks test youtube_data_pipeline save_to_rds_task '2023-01-01'
