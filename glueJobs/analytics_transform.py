import sys
import logging
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get job arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_path', 'target_path'])
# source_path example: s3://your-bucket/processed/year=YYYY/month=MM/
# target_path example: s3://your-bucket/analytics-ready/year=YYYY/month=MM/

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

try:
    logger.info("Reading JSON data from %s", args['source_path'])
    # Read JSON files into a Spark DataFrame
    df = spark.read.json(args['source_path'])
    
    # Optional: You can perform additional transformations here if needed.
    
    # Convert DataFrame to DynamicFrame
    dynamic_frame = DynamicFrame.fromDF(df, glueContext, "dynamic_frame")
    
    logger.info("Writing analytics-ready data as Parquet to %s", args['target_path'])
    # Write output as Parquet to target S3 path
    glueContext.write_dynamic_frame.from_options(
        frame = dynamic_frame,
        connection_type = "s3",
        connection_options = {"path": args['target_path'], "partitionKeys": []},
        format = "parquet"
    )
    
    logger.info("AnalyticsTransformJob completed successfully.")
except Exception as e:
    logger.error("Error in AnalyticsTransformJob: %s", str(e))
    raise

sc.stop()
