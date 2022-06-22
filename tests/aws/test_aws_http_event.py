import json
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from clubbi_utils.aws.aws_http_event import AwsHttpEvent

PARENT_DIR = Path(__file__).parent


class TestAwsHttpEvent(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        super().setUp()
    data = json.loads(PARENT_DIR.joinpath("local_mocks/static/aws_http_payload_v2.json").read_text())

        self.payload = data
        self.event: AwsHttpEvent = data

    def test_parse_aws_http_event(self):
        assert self.event == AwsHttpEvent(
            body="Hello from Lambda",
            headers={"header1": "value1", "header2": "value1,value2"},
            queryStringParameters={"parameter1": "value1,value2", "parameter2": "value"},
            pathParameters={"parameter1": "value1"}
        )

    def test_get_path_parameters(self):
        path_params = self.event.get("pathParameters")

        assert path_params
        assert path_params.get("parameter1") == self.payload['pathParameters']['parameter1']
