from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    CfnOutput,
    Tags
)
from constructs import Construct
from typing import Any, Dict
import os

class S3PresignedurlStack(Stack):

   def __init__(self, scope: Construct, construct_id: str, config: Dict[str, Any], **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # Environment-based configuration
    environment = self.node.try_get_context("environment") or "dev"
    
    # Add stack tags
    Tags.of(self).add("Environment", environment)
    Tags.of(self).add("Project", "PresignedUrlService")
    Tags.of(self).add("ManagedBy", "CDK")

    # Create S3 bucket with best practices
    bucket = s3.Bucket(
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
            allowed_origins=config["allowed_origins"],
            allowed_headers=["*"],
            max_age=Duration.hours(1)
        )],
        lifecycle_rules=[
            s3.LifecycleRule(
                enabled=True,
                expiration=Duration.days(config["file_expiration_days"]),
                noncurrent_version_expiration=Duration.days(30)
            )
        ]
    )

    # Create Lambda function with best practices
    lambda_fn = _lambda.Function(
        self,
        "PresignedUrlGenerator",
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler="lambda_function.handler",
        code=_lambda.Code.from_asset("lambda"),
        environment={
            "BUCKET_NAME": bucket.bucket_name,
            "ENVIRONMENT": environment,
            "MAX_FILE_SIZE": str(config["max_file_size_mb"]),
            "URL_EXPIRATION": str(config["url_expiration_seconds"])
        },
        timeout=Duration.seconds(30),
        memory_size=256,
        tracing=_lambda.Tracing.ACTIVE,
        log_retention=logs.RetentionDays.ONE_MONTH,
        architecture=_lambda.Architecture.ARM_64,
        description="Generates presigned URLs for S3 file uploads"
    )

    # Grant Lambda permissions to generate presigned URLs
    bucket.grant_read_write(lambda_fn)

    # Create API Gateway with best practices
    api = apigw.RestApi(
        self,
        "PresignedUrlApi",
        rest_api_name=f"PresignedUrlGenerator-{environment}",
        deploy_options=apigw.StageOptions(
            stage_name=environment,
            throttling_rate_limit=config["api_rate_limit"],
            throttling_burst_limit=config["api_burst_limit"],
            logging_level=apigw.MethodLoggingLevel.INFO,
            metrics_enabled=True,
            tracing_enabled=True
        ),
        default_cors_preflight_options=apigw.CorsOptions(
            allow_origins=config["allowed_origins"],
            allow_methods=["GET", "OPTIONS"],
            allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
            max_age=Duration.hours(1)
        )
    )

    # Add API Gateway Resource and Method
    generate_url = api.root.add_resource("generate-url")
    
    # Add request validation
    validator = api.add_request_validator(
        "QueryStringValidator",
        validate_request_parameters=True
    )

    # Add method with validation
    generate_url.add_method(
        "GET",
        apigw.LambdaIntegration(
            lambda_fn,
            proxy=True,
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            }]
        ),
        request_parameters={
            "method.request.querystring.filename": True,
            "method.request.querystring.contentType": False
        },
        request_validator=validator,
        method_responses=[
            apigw.MethodResponse(
                status_code="200",
                response_parameters={
                    'method.response.header.Access-Control-Allow-Origin': True
                }
            )
        ]
    )

    # Add CloudFormation outputs
    CfnOutput(
        self,
        "ApiEndpoint",
        value=f"{api.url}generate-url",
        description="API Endpoint URL"
    )
    
    CfnOutput(
        self,
        "BucketName",
        value=bucket.bucket_name,
        description="Upload Bucket Name"
    )