from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# Calculate the directory of the current file to make paths relative to this location
current_file_dir = os.path.dirname(os.path.abspath(__file__))

def ingest_data(channel_id):
    # Construct the relative path to the ingestion script
    script_path = os.path.join(current_file_dir, 'ingestion', 'video_data_collector.py')
    os.system(f'python {script_path} --channel_id {channel_id}')

def upload_to_s3(channel_name):
    # Construct the relative path to the upload script
    script_path = os.path.join(current_file_dir, 'ingestion', 'upload_to_s3.py')
    os.system(f'python {script_path} --channel_name {channel_name}')


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'youtube_data_pipeline',
    default_args=default_args,
    description='A pipeline to collect and process YouTube video data',
    schedule_interval='@once',
    catchup=False, # ensure that the DAG does not backfill, backfill means to run all the historical data
)

ingest_task = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest_data,
    op_kwargs={'channel_id': 'UCvysUcwPV3LppVzfxkIGXhg'},  #UCwdogH5kbb9wGy2Amvw6KeQ
    dag=dag,
)

upload_task = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    op_kwargs={'channel_name': 'my_channel'},
    dag=dag,
)

ingest_task >> upload_task