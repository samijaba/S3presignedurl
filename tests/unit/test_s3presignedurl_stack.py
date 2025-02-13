import aws_cdk as core
import aws_cdk.assertions as assertions

from s3presignedurl.s3presignedurl_stack import S3PresignedurlStack

# example tests. To run these tests, uncomment this file along with the example
# resource in s3presignedurl/s3presignedurl_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = S3PresignedurlStack(app, "s3presignedurl")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
