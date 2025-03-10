import sys
import datetime
import logging
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql.functions import current_timestamp, lit

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get job arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_path', 'target_path'])
# source_path example: s3://your-bucket/raw/
# target_path example: s3://your-bucket/processed/year=YYYY/month=MM/

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

try:
    logger.info("Reading CSV data from %s", args['source_path'])
    # Read CSV files into a Spark DataFrame; infer schema automatically
    df = spark.read.option("header", "true").csv(args['source_path'])
    
    # Basic transformation: add processed_timestamp column
    df_transformed = df.withColumn("processed_timestamp", current_timestamp())
    
    # Optional: Perform additional cleanup or type casting as needed.
    
    # Convert DataFrame back to DynamicFrame
    dynamic_frame = DynamicFrame.fromDF(df_transformed, glueContext, "dynamic_frame")
    
    logger.info("Writing processed data as JSON to %s", args['target_path'])
    # Write output as JSON to target S3 path
    glueContext.write_dynamic_frame.from_options(
        frame = dynamic_frame,
        connection_type = "s3",
        connection_options = {"path": args['target_path'], "partitionKeys": []},
        format = "json"
    )
    
    logger.info("ProcessCSVJob completed successfully.")
except Exception as e:
    logger.error("Error in ProcessCSVJob: %s", str(e))
    raise

sc.stop()
