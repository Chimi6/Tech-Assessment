import json
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_kms as kms,
)
from constructs import Construct

class MyCompanyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load the list of customers from the external file
        with open("customers.json", "r") as f:
            customers = json.load(f)

        # Create a KMS key for encrypting all customer buckets
        kms_key = kms.Key(self, "MyCompanyKmsKey",
                          enable_key_rotation=True,
                          alias="mycompany-kms-key")

        # Loop over each customer and create an S3 bucket with required configuration
        for customer in customers:
            s3.Bucket(
                self, f"Bucket-{customer}",
                bucket_name=f"mycompany-{customer}-prod-datalake",
                encryption=s3.BucketEncryption.KMS,
                encryption_key=kms_key,
                removal_policy=RemovalPolicy.RETAIN,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            )
