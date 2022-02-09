from typing import List, Any
from unittest import IsolatedAsyncioTestCase
from aiobotocore.client import AioBaseClient
from unittest.mock import MagicMock, AsyncMock
from asyncio import StreamReader
from pydantic import BaseModel
from clubbi_utils import json

from clubbi_utils.aws.lambda_invoker import (
    AwsLambdaInvoker,
    LambdaRaisedAnExceptionError,
    LambdaFailedToParseOutputError,
)


def create_lambda_aiobotocore_mock(lambda_payload_response: str) -> AioBaseClient:
    mock = MagicMock()

    stream_reader = MagicMock(StreamReader)
    stream_reader.read.return_value = lambda_payload_response.encode()
    mock.invoke = AsyncMock()
    mock.invoke.return_value = dict(
        Payload=stream_reader,
    )
    return mock


class _Input(BaseModel):
    args: List[str]


class _Output(BaseModel):
    ans: int


class TestLambdaInvoker(IsolatedAsyncioTestCase):
    async def test_successfull_invocation(self):
        expected_output = _Output(ans=2)
        invoker = AwsLambdaInvoker[_Input, _Output](
            aws_lambda_client := create_lambda_aiobotocore_mock(expected_output.json()),
            function_name := "cool_function",
        )

        output = await invoker(input := _Input(args=["oi", "hi"]))

        self.assertEqual(output, expected_output)

        aws_lambda_client.invoke.assert_awaited_once_with(
            FunctionName=function_name,
            Payload=json.dumps(input).encode(),
        )

    async def test_lambda_raising_exception(self):
        payload = dict(
            errorType="testType",
            requestId="123",
            stackTrace=["line1", "line2"],
            errorMessage="error",
        )
        err = LambdaRaisedAnExceptionError("cool_function", payload)

        invoker = AwsLambdaInvoker[Any, Any](
            aws_lambda_client=create_lambda_aiobotocore_mock(json.dumps(payload)),
            function_name="cool_function",
        )

        with self.assertRaises(LambdaRaisedAnExceptionError) as e:
            await invoker("a")

        self.assertEqual(err, e.exception)

    async def test_lambda_resturning_invalid_payoload(self):
        output = dict(a=2, b=["1", "2"])
        invoker = AwsLambdaInvoker[Any, _Output](
            aws_lambda_client=create_lambda_aiobotocore_mock(json.dumps(output)),
            function_name="cool_function",
        )

        with self.assertRaises(LambdaFailedToParseOutputError) as e:
            a = await invoker("a")

        self.assertEqual(
            e.exception,
            LambdaFailedToParseOutputError(
                function_name="cool_function", output=output
            ),
        )
