import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, expr, to_timestamp
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame


args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from AWS Glue Data Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(database="video-analytics", table_name="video_data_json", transformation_ctx="datasource")

# Convert DynamicFrame to DataFrame for more complex operations
df = datasource.toDF()

# Perform transformations: cast numeric fields, handle nulls if necessary
df = df.withColumn("view_count", col("view_count").cast("int"))
df = df.withColumn("like_count", col("like_count").cast("int"))
df = df.withColumn("comment_count", col("comment_count").cast("int"))
df = df.withColumn("publish_time", to_timestamp(col("publish_time"), "yyyy-MM-dd'T'HH:mm:ss'Z'"))

# Remove duplicates based on `video_id`
# Assuming that in case of duplicates, you want to keep the first occurrence
df = df.dropDuplicates(['video_id'])

# Calculate additional metrics
# Total views, likes, and comments
total_views = df.agg({"view_count": "sum"}).collect()[0][0]
total_likes = df.agg({"like_count": "sum"}).collect()[0][0]
total_comments = df.agg({"comment_count": "sum"}).collect()[0][0]

# Average likes and views per video
average_likes = df.agg({"like_count": "avg"}).collect()[0][0]
average_views = df.agg({"view_count": "avg"}).collect()[0][0]

# Engagement rate: (likes + comments) / views
df = df.withColumn("engagement_rate", expr("(like_count + comment_count) / view_count"))

# Top performing videos by likes
top_videos_by_likes = df.orderBy(col("like_count").desc()).limit(10)

# Convert back to DynamicFrame
processed_datasource = DynamicFrame.fromDF(df, glueContext, "processed_datasource")
top_videos_dynamicframe = DynamicFrame.fromDF(top_videos_by_likes, glueContext, "top_videos_dynamicframe")

# Write the processed data back to S3 in Parquet format
sink = glueContext.write_dynamic_frame.from_options(frame = processed_datasource, connection_type = "s3", connection_options = {"path": "s3://video-analytics-goalcast/processed/"}, format = "parquet", transformation_ctx = "sink")

# Optionally, you can also write the top videos by likes back to S3 in Parquet format
sink_top_videos = glueContext.write_dynamic_frame.from_options(frame = top_videos_dynamicframe, connection_type = "s3", connection_options = {"path": "s3://video-analytics-goalcast/top_videos/"}, format = "parquet", transformation_ctx = "sink_top_videos")

job.commit()
