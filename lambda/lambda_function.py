import os
import json
import boto3
from typing import Dict, Any

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler to generate presigned URLs for S3 file uploads."""
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters', {})
        if not query_params or 'filename' not in query_params:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Filename parameter is required'})
            }
        
        filename = query_params['filename']
        
        # Get environment variables
        bucket_name = os.environ['BUCKET_NAME']
        max_file_size = int(os.environ.get('MAX_FILE_SIZE', '100')) * 1024 * 1024  # MB to bytes
        url_expiration = int(os.environ.get('URL_EXPIRATION', '3600'))  # seconds

        # Generate presigned URL
        s3_client = boto3.client('s3')
        
        # Add conditions for the presigned URL
        

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': filename
            },
            ExpiresIn=url_expiration
        )
        
        return {
            'statusCode': 200,
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type"
        },
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'expiresIn': url_expiration
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }