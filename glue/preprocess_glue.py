import sys
import logging
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, expr, to_timestamp
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame

# Setup logging
logging.basicConfig(level=logging.DEBUG)

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

try:
    # Read data from AWS Glue Data Catalog
    datasource = glueContext.create_dynamic_frame.from_catalog(database="video-analytics", table_name="video_data_json", transformation_ctx="datasource")
    df = datasource.toDF()

    # Data transformations
    df = df.withColumn("view_count", col("view_count").cast("int"))
    df = df.withColumn("like_count", col("like_count").cast("int"))
    df = df.withColumn("comment_count", col("comment_count").cast("int"))
    df = df.withColumn("publish_time", to_timestamp(col("publish_time"), "yyyy-MM-dd'T'HH:mm:ss'Z'"))
    df = df.dropDuplicates(['video_id'])

    # Log total count of records processed
    logger.info(f"Total records processed: {df.count()}")

    # Calculations
    total_views = df.agg({"view_count": "sum"}).collect()[0][0]
    total_likes = df.agg({"like_count": "sum"}).collect()[0][0]
    total_comments = df.agg({"comment_count": "sum"}).collect()[0][0]
    df = df.withColumn("engagement_rate", expr("(like_count + comment_count) / view_count"))

    # Writing to S3
    processed_path = "s3://video-analytics-goalcast/processed/"
    top_videos_path = "s3://video-analytics-goalcast/top_videos/"
    df.write.parquet(processed_path, mode="overwrite")
    df.orderBy(col("like_count").desc()).limit(10).write.parquet(top_videos_path, mode="overwrite")

    job.commit()
except Exception as e:
    logger.error("An error occurred in the Glue job", exc_info=True)
    job.commit(status='FAILED')
