# Docs https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html
from typing import Dict, TypedDict


class AwsLambdaHttpRequestEvent(TypedDict):
    body: str
    headers: Dict[str, str]


class AwsLambdaHttpResponse(TypedDict):
    statusCode: int
    body: str
    headers: Dict[str, str]
