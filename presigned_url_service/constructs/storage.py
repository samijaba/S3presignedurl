from constructs import Construct
from aws_cdk import (
    aws_s3 as s3,
    RemovalPolicy,
    Duration,
    Tags
)
from typing import List

class StorageConstruct(Construct):
    def __init__(self, scope: Construct, id: str, 
                 environment: str,
                 allowed_origins: List[str],
                 file_expiration_days: int,
                 **kwargs) -> None:
        super().__init__(scope, id)

        self.bucket = s3.Bucket(
            self, 
            "UploadBucket",
            removal_policy=RemovalPolicy.RETAIN if environment == "prod" else RemovalPolicy.DESTROY,
            auto_delete_objects=environment != "prod",
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT],
                allowed_origins=allowed_origins,
                allowed_headers=["*"]
            )],
            lifecycle_rules=[
                s3.LifecycleRule(
                    enabled=True,
                    expiration=Duration.days(file_expiration_days),
                    noncurrent_version_expiration=Duration.days(30)
                )
            ]
        )

        Tags.of(self.bucket).add("Environment", environment)
        Tags.of(self.bucket).add("Service", "PresignedUrlService")

