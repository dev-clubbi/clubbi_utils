from typing import Dict, List, TypedDict


class AwsSqsRecord(TypedDict):
    messageId: str
    body: str
    eventSource: str


class AwsSqsEvent(TypedDict):
    Records: List[AwsSqsRecord]
