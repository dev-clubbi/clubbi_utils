from typing import Optional, TypedDict, Dict, List

__all__ = [
    "AwsHttpEvent",
    "AwsHttpResponse"
]

# Aws payload format version 2.0 (simplified)
# REF.: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html


class AwsHttpEvent(TypedDict, total=False):
    body: str
    headers: Dict[str, str]
    queryStringParameters: Dict[str, str]
    pathParameters: Dict[str, str]


class AwsHttpResponse(TypedDict, total=False):
    statusCode: int
    body: Optional[str]
    headers: Optional[Dict[str, str]]
    cookies: Optional[List[str]]
    isBase64Encoded: Optional[bool]
