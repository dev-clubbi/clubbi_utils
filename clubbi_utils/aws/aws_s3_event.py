# Docs: https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html#with-s3-example-test-dummy-event
from typing import TypedDict, List


class AwsS3EventBucket(TypedDict):
    name: str
    arn: str


class AwsS3EventObject(TypedDict):
    key: str
    size: int
    eTag: str
    sequencer: str


class AwsS3EventInfo(TypedDict):
    s3SchemaVersion: str
    configurationId: str
    bucket: AwsS3EventBucket
    object: AwsS3EventObject


class AwsS3EventRecord(TypedDict):
    eventVersion: str
    eventSource: str
    awsRegion: str
    eventTime: str
    eventName: str
    s3: AwsS3EventInfo


class AwsS3Event(TypedDict):
    Records: List[AwsS3EventRecord]
