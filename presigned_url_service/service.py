from constructs import Construct
from aws_cdk import CfnOutput
from typing import Dict, Any

from .constructs import StorageConstruct, LambdaConstruct, ApiConstruct

class PresignedUrlService(Construct):
    def __init__(self, scope: Construct, id: str,
                 environment: str,
                 config: Dict[str, Any],
                 **kwargs) -> None:
        super().__init__(scope, id)

        # Create storage construct
        storage = StorageConstruct(
            self, 'Storage',
            environment=environment,
            allowed_origins=config["allowed_origins"],
            file_expiration_days=config["file_expiration_days"]
        )

        # Create lambda construct
        lambda_construct = LambdaConstruct(
            self, 'Lambda',
            environment=environment,
            environment_vars={
                "BUCKET_NAME": storage.bucket.bucket_name,
                "ENVIRONMENT": environment,
                "MAX_FILE_SIZE": str(config["max_file_size_mb"]),
                "URL_EXPIRATION": str(config["url_expiration_seconds"])
            }
        )

        # Grant Lambda permissions to the bucket
        storage.bucket.grant_read_write(lambda_construct.function)

        # Create API construct
        api = ApiConstruct(
            self, 'Api',
            environment=environment,
            allowed_origins=config["allowed_origins"],
            rate_limit=config["api_rate_limit"],
            burst_limit=config["api_burst_limit"],
            lambda_function=lambda_construct.function
        )

        # Add CloudFormation outputs
        CfnOutput(
            self,
            "ApiEndpoint",
            value=f"{api.api.url}generate-url",
            description="API Endpoint URL"
        )
        
        CfnOutput(
            self,
            "BucketName",
            value=storage.bucket.bucket_name,
            description="Upload Bucket Name"
        )