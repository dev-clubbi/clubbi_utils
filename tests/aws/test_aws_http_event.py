import json
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from clubbi_utils.aws.aws_http_event import AwsHttpEvent

STATIC_DIR = Path(__file__).parent


class TestAwsHttpEvent(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        super().setUp()
        with STATIC_DIR.joinpath("local_mocks/static/aws_http_payload_v2.json").open() as jsonfile:
            data = json.load(jsonfile)

        self.payload = data

    def test_parse_aws_http_event(self):
        event: AwsHttpEvent = self.payload

        assert event == AwsHttpEvent(
            body="Hello from Lambda",
            headers={"header1": "value1", "header2": "value1,value2"},
            queryStringParameters={"parameter1": "value1,value2", "parameter2": "value"},
            pathParameters={"parameter1": "value1"}
        )
