# Docs: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs-example.html#with-sqs-create-test-function
from typing import Dict, List, TypedDict


class AwsSqsRecord(TypedDict):
    messageId: str
    body: str
    eventSource: str


class AwsSqsEvent(TypedDict):
    Records: List[AwsSqsRecord]
