class AwsHttpEvent(TypedDict):
    headers: Dict[str, str]
    queryStringParameters: Optional[Dict[str, str]]


class AwsHttpResponse(TypedDict):
    statusCode: int
    body: str
    headers: Dict[str, str]
