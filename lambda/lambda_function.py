import boto3
import os
import json
import re
from typing import Dict, Any, Optional
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

class FileUploadError(Exception):
    pass

class ConfigurationError(Exception):
    pass

def validate_filename(filename: str) -> bool:
    """Validate filename for security and compatibility."""
    if not filename or len(filename) > 255:
        return False
    
    # Restrict to alphanumeric, hyphens, underscores, and common extensions
    pattern = r'^[\w\-]+\.[A-Za-z0-9]+$'
    return bool(re.match(pattern, filename))

def get_content_type(filename: str) -> str:
    """Get content type based on file extension."""
    extension_map = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'txt': 'text/plain'
    }
    ext = filename.split('.')[-1].lower()
    return extension_map.get(ext, 'application/octet-stream')

@app.get("/generate-url")
@tracer.capture_method
def generate_presigned_url(filename: Optional[str] = None) -> Dict[str, Any]:
    """Generate a presigned URL for file upload."""
    try:
        if not filename:
            raise FileUploadError("Filename parameter is required")

        if not validate_filename(filename):
            raise FileUploadError("Invalid filename format")

        bucket_name = os.environ['BUCKET_NAME']
        max_file_size = int(os.environ.get('MAX_FILE_SIZE', 100)) * 1024 * 1024  # MB to bytes
        url_expiration = int(os.environ.get('URL_EXPIRATION', 3600))  # seconds

        s3_client = boto3.client('s3')
        
        # Generate presigned URL with content type and size conditions
        conditions = [
            ['content-length-range', 0, max_file_size]
        ]

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': filename,
                'ContentType': get_content_type(filename)
            },
            ExpiresIn=url_expiration,
            Conditions=conditions
        )

        metrics.add_metric(name="PresignedUrlGenerated", unit="Count", value=1)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            },
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'expiresIn': url_expiration,
                'maxFileSize': max_file_size
            })
        }

    except Exception as e:
        logger.exception("Error generating presigned URL")
        metrics.add_metric(name="PresignedUrlError", unit="Count", value=1)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Lambda handler with observability decorators."""
    return app.resolve(event, context)