from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_logs as logs,
    Duration,
    Tags
)
from typing import Dict

class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str,
                 environment: str,
                 environment_vars: Dict[str, str],
                 **kwargs) -> None:
        super().__init__(scope, id)

        self.function = _lambda.Function(
            self,
            "PresignedUrlGenerator",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment=environment_vars,
            timeout=Duration.seconds(30),
            memory_size=256,
            tracing=_lambda.Tracing.ACTIVE,
            log_retention=logs.RetentionDays.ONE_MONTH,
            architecture=_lambda.Architecture.ARM_64,
            description="Generates presigned URLs for S3 file uploads"
        )

        Tags.of(self.function).add("Environment", environment)
        Tags.of(self.function).add("Service", "PresignedUrlService")
