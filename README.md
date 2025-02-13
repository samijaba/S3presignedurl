# Secure Presigned URL Generator - AWS CDK Project

## Overview

This project implements a secure and scalable infrastructure for generating presigned URLs for S3 file uploads using AWS CDK. It follows AWS best practices and includes comprehensive security features, monitoring, and error handling.

## Architecture

The project creates the following AWS resources:
- S3 bucket with encryption, versioning, and lifecycle policies
- Lambda function with monitoring and tracing enabled
- API Gateway with request validation and rate limiting
- Comprehensive IAM permissions following least privilege principle

## Security Features

- Server-side encryption for S3 bucket
- SSL enforcement for S3 access
- Block all public access to S3 bucket
- CORS configuration with restrictive settings
- Request validation in API Gateway
- Rate limiting and burst control
- Filename validation and sanitization
- Content type enforcement
- File size limits
- URL expiration control
- Environment-based configuration

## Prerequisites

- AWS CLI configured with appropriate credentials
- Node.js 14.x or later
- Python 3.9 or later
- AWS CDK CLI 2.x or later
- Docker (for local testing)

## Project Structure

```
.
├── app.py                 # CDK app entry point
├── lambda/
│   └── lambda_function.py # Lambda function code
├── config/
│   └── config.json       # Environment configurations
├── tests/                # Test directory
├── cdk.json             # CDK configuration
└── requirements.txt     # Python dependencies
```

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment settings in `config/config.json`

4. Deploy the stack:
```bash
# For development
cdk deploy -c environment=dev

# For production
cdk deploy -c environment=prod
```

## Usage

### Generating a Presigned URL

Make a GET request to the API endpoint:

```bash
curl "https://[api-gateway-url]/generate-url?filename=example.pdf"
```

Response format:
```json
{
    "uploadUrl": "https://[presigned-url]",
    "expiresIn": 3600,
    "maxFileSize": 104857600
}
```

### Uploading a File

Use the presigned URL to upload your file:

```bash
curl -X PUT -H "Content-Type: application/pdf" \
     --upload-file ./example.pdf \
     "[presigned-url]"
```

## Monitoring and Logging

The project includes:
- CloudWatch Logs for Lambda and API Gateway
- X-Ray tracing
- Custom metrics using CloudWatch
- AWS Lambda Powertools for enhanced observability

## Best Practices Implemented

1. Security:
   - Encryption at rest
   - SSL enforcement
   - Strict CORS policies
   - Input validation
   - Rate limiting

2. Reliability:
   - Error handling
   - Retry mechanisms
   - Request validation
   - Monitoring and alerting

3. Performance:
   - ARM64 architecture for Lambda
   - Optimized memory allocation
   - Content type optimization

4. Cost Optimization:
   - Lifecycle policies
   - Log retention policies
   - Resource cleanup

5. Operational Excellence:
   - Environment-based configuration
   - Comprehensive logging
   - Tracing enabled
   - Metrics collection

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/
```

## Cleanup

To remove the deployed resources:

```bash
cdk destroy -c environment=dev  # or prod
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Considerations

1. Production Deployment:
   - Restrict CORS origins to your domain
   - Enable WAF for API Gateway
   - Implement authentication
   - Use custom domains with SSL/TLS
   - Enable AWS Organizations SCPs

2. File Upload Security:
   - Implement virus scanning
   - Set up file type validation
   - Configure max file size limits
   - Enable versioning for recovery

3. Access Control:
   - Implement IAM roles
   - Use AWS KMS for encryption
   - Enable VPC endpoints
   - Configure network ACLs

## Troubleshooting

Common issues and solutions:

1. Deployment Failures:
   - Check AWS credentials
   - Verify account limits
   - Review CloudFormation logs

2. Upload Errors:
   - Verify content type
   - Check file size limits
   - Validate CORS settings
   - Review Lambda logs

3. Permission Issues:
   - Check IAM roles
   - Verify bucket policies
   - Review security groups

## Support

For support and questions:
1. Open an issue in the repository
2. Review existing issues
3. Check AWS documentation
4. Contact AWS support

## Future Enhancements

Planned improvements:
1. Multi-region deployment
2. Enhanced monitoring
3. Automated testing
4. CI