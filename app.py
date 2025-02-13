from aws_cdk import App, Stack, Environment
from constructs import Construct
from presigned_url_service.service import PresignedUrlService
import json

class MainStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        environment = self.node.try_get_context("environment") or "dev"
        
        # Load configuration
        with open('config/config.json', 'r') as f:
            config = json.load(f)[environment]

        # Create the presigned URL service construct
        PresignedUrlService(self, 'PresignedUrlService', 
            environment=environment,
            config=config
        )

app = App()
MainStack(app, "PresignedUrlServiceStack")
app.synth()