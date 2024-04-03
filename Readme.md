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

Optional:
5. Set up a scheduled job to run the `video_data_collector.py` script at regular intervals to keep the video data up-to-date. 

6. Setup AWS Glue to read the data from S3 and store it in a database for further analysis.
 - Create a crawler to read the data from S3 and store it in a database.
 - Optional: Create a scheduled job to run the crawler at regular intervals to keep the data up-to-date.
 - Run a ETL job to transform the data and store it in the processed S3 bucket.

7. Provision an AWS RDS Instance
 - We chose PostgreSQL as our database engine (use version 13.10 for glue connector compatibility).
 - After your RDS instance is up and running, note down the endpoint URL, database name, username, and password, as you'll need these for connecting to the database.

8. Connect to the RDS instance using psql, if you didn't install it already, you can install it using the following command:
   ```bash
   sudo yum install postgresql15
   ```
   ```bash
   psql -h <endpoint-url> -U <username> -d <database-name>
   ```
   Alternatively
   ```bash
   psql --host=<> --port=5432 --username=postgres --password --dbname=<database-name>
   ```

9. Create a table in the RDS instance to store the video data.
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
   ```
   ```sql
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
10. Create a Glue job to read the data from the S3 bucket and store it in the RDS instance.
    1.  Create a new Glue job.
    2.  Choose the IAM role and add AmazonRDSFullAccess policy to the role.
    3.  The script is inside the `aws-glue-script.py` file.
    4.  Setup a glue connector in Data connections and choose data source as postgresql. 
    5.  Run the job.


11. Setup Airflow to schedule everything.
    ```bash
    pip install "apache-airflow[celery]==2.8.4" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.4/constraints-3.8.txt"
    pip install apache-airflow-providers-amazon
    ```
    ```bash
    airflow standalone
    ```
    Now you can boot up the webserver and scheduler.
    ```bash
    airflow webserver
    ```
    ```bash
    airflow scheduler
    ```
    You can access the webserver at `http://localhost:8080/` and the scheduler will run the jobs at the scheduled time. 
    It is important to set the environment variables for the AWS credentials and Google API KEY in the airflow UI.