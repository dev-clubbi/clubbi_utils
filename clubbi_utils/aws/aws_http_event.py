from typing import Optional, TypedDict, Dict

__all__ = [
    "AwsHttpEvent",
    "AwsHttpResponse"
]


class RequestContext(TypedDict, total=False):
    authentication: Dict[str, str]
    authorizer: Dict[str, str]


# Aws payload format version 2.0 (simplified)
# REF.: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
class AwsHttpEvent(TypedDict, total=False):
    body: str
    headers: Dict[str, str]
    queryStringParameters: Optional[Dict[str, str]]
    pathParameters: Dict[str, str]
    requestContext: RequestContext


class AwsHttpResponse(TypedDict, total=False):
    statusCode: int
    headers: Dict[str, str]
    body: Optional[str]

