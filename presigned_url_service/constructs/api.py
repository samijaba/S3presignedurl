from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    Duration,
    Tags
)
from typing import List

class ApiConstruct(Construct):
    def __init__(self, scope: Construct, id: str,
                 environment: str,
                 allowed_origins: List[str],
                 rate_limit: int,
                 burst_limit: int,
                 lambda_function: _lambda.Function,
                 **kwargs) -> None:
        super().__init__(scope, id)

        self.api = apigw.RestApi(
            self,
            "PresignedUrlApi",
            rest_api_name=f"PresignedUrlGenerator-{environment}",
            deploy_options=apigw.StageOptions(
                stage_name=environment,
                throttling_rate_limit=rate_limit,
                throttling_burst_limit=burst_limit,
                metrics_enabled=True,
                tracing_enabled=True
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=allowed_origins,
                allow_methods=["GET", "OPTIONS"],
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
                max_age=Duration.hours(1)
            )
        )

        # Add request validation
        validator = self.api.add_request_validator(
            "QueryStringValidator",
            validate_request_parameters=True
        )

        # Add API Gateway Resource and Method
        generate_url = self.api.root.add_resource("generate-url")
        generate_url.add_method(
            "GET",
            apigw.LambdaIntegration(
                lambda_function,
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

        Tags.of(self.api).add("Environment", environment)
        Tags.of(self.api).add("Service", "PresignedUrlService")

