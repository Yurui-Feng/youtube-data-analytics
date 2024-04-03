import sys
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql.functions import col, to_timestamp, unix_timestamp, from_unixtime

# Initialization
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Connection name
connection_name = "rds-connector"  # Adjust this to your Glue connection's name

# Read and write video_data to RDS
s3_path_processed = "s3://video-analytics-goalcast/processed/"
datasource_processed = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [s3_path_processed]},
    format="parquet"
)

# Convert to DataFrame
df_processed = datasource_processed.toDF()
# df_processed = df_processed.withColumn("publish_time", to_timestamp("publish_time", "yyyy-MM-dd'T'HH:mm:ss'Z'"))

# Utilize the Glue Connection to write the DataFrame to RDS
glueContext.write_dynamic_frame.from_jdbc_conf(
    frame=DynamicFrame.fromDF(df_processed, glueContext, "df_processed"),
    catalog_connection=connection_name,
    connection_options={"dbtable": "video_data", "database": "ytb_goalcast"},
    transformation_ctx="write_processed_data"
)

# Read and write top_videos to RDS
s3_path_top_videos = "s3://video-analytics-goalcast/top_videos/"
datasource_top_videos = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [s3_path_top_videos]},
    format="parquet"
)

# Convert to DataFrame
df_top_videos = datasource_top_videos.toDF()
# df_top_videos = df_top_videos.withColumn("publish_time", to_timestamp("publish_time", "yyyy-MM-dd'T'HH:mm:ss'Z'"))

# Utilize the Glue Connection to write the DataFrame to RDS
glueContext.write_dynamic_frame.from_jdbc_conf(
    frame=DynamicFrame.fromDF(df_top_videos, glueContext, "df_top_videos"),
    catalog_connection=connection_name,
    connection_options={"dbtable": "top_videos", "database": "ytb_goalcast"},
    transformation_ctx="write_top_videos"
)

job.commit()
