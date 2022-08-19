from datetime import datetime
from clubbi_utils import json
from typing import Any, Dict
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from pydantic import BaseModel, ValidationError

from clubbi_utils.aws.get_ssm_secret import GetSecretValueResponse, get_ssm_secret


class MyBaseModel(BaseModel):
    a: str
    i: int


class TestGetSsmSecret(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._ssm_client = AsyncMock()

    def _set_ssm_client_response(self, secret_string: str) -> None:
        self._ssm_client.get_secret_value.return_value = GetSecretValueResponse(
            ARN="",
            Name="",
            VersionId="",
            SecretBinary=b"",
            SecretString=secret_string,
            VersionStages=[],
            CreatedDate=datetime(2022, 2, 2),
        )

    async def test_successful_ssm_call_on_str(self):
        self._set_ssm_client_response(secret_value := "Hello World")
        actual_res = await get_ssm_secret(self._ssm_client, secret_key := "my/secret/name")

        self.assertEqual(actual_res, secret_value)
        self._ssm_client.get_secret_value.awaited_once_with(SecretId=secret_key)

    async def test_successful_ssm_call_on_dict(self):
        res = dict(a="a", i=2)
        self._set_ssm_client_response(json.dumps(res))

        actual_res = await get_ssm_secret(self._ssm_client, "my/secret/name", Dict[str, Any])
        self.assertEqual(res, actual_res)

    async def test_successful_ssm_call_on_base_model(self):
        res = MyBaseModel(a="a", i=2)
        self._set_ssm_client_response(res.json())

        actual_res = await get_ssm_secret(self._ssm_client, "my/secret/name", MyBaseModel)
        self.assertEqual(res, actual_res)

    async def test_unsuccessful_ssm_call_parse_error(self):
        self._set_ssm_client_response(json.dumps(dict(a="a")))

        with self.assertRaises(ValidationError):
            await get_ssm_secret(self._ssm_client, "my/secret/name", MyBaseModel)

    async def test_unsuccessful_ssm_call_aws_error(self):
        err = self._ssm_client.get_secret_value.side_effect = RuntimeError("Test")

        with self.assertRaises(RuntimeError) as act_err:
            await get_ssm_secret(self._ssm_client, "my/secret/name")

        self.assertEqual(act_err.exception, err)
