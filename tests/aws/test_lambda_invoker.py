from typing import List, Any, cast
from unittest import IsolatedAsyncioTestCase
from aiobotocore.client import AioBaseClient
from unittest.mock import MagicMock, AsyncMock
from asyncio import StreamReader
from pydantic import BaseModel
from clubbi_utils import json

from clubbi_utils.aws.lambda_invoker import (
    AwsLambdaInvoker,
    InvalidInputType,
    LambdaRaisedAnExceptionError,
    FailedToParseOutputError,
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
        invoker = AwsLambdaInvoker(
            aws_lambda_client := create_lambda_aiobotocore_mock(expected_output.json()),
            function_name := "cool_function",
            input_type=_Input,
            output_type=_Output,
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

        invoker = AwsLambdaInvoker(
            aws_lambda_client=create_lambda_aiobotocore_mock(json.dumps(payload)),
            function_name="cool_function",
            input_type=object,
            output_type=object,
        )

        with self.assertRaises(LambdaRaisedAnExceptionError) as e:
            await invoker("a")

        self.assertEqual(err, e.exception)

    async def test_lambda_returning_invalid_payload(self):
        output = dict(a=2, b=["1", "2"])
        invoker = AwsLambdaInvoker(
            aws_lambda_client=create_lambda_aiobotocore_mock(json.dumps(output)),
            function_name="cool_function",
            input_type=object,
            output_type=_Output,
        )

        with self.assertRaises(FailedToParseOutputError) as e:
            a = await invoker("a")

        self.assertEqual(
            e.exception,
            FailedToParseOutputError(function_name="cool_function", output=output),
        )

    async def test_invalid_input(self):
        invoker = AwsLambdaInvoker(
            aws_lambda_client=create_lambda_aiobotocore_mock(""),
            function_name="cool_function",
            input_type=_Input,
            output_type=_Output,
        )

        with self.assertRaises(InvalidInputType) as e:
            input_ = cast(Any, "nada")
            await invoker(input_)

    async def test_primitive_input_types(self):
        expected_output = ["hello", "world"]
        invoker = AwsLambdaInvoker(
            aws_lambda_client := create_lambda_aiobotocore_mock(json.dumps(expected_output)),
            function_name := "cool_function",
            input_type=List[int],
            output_type=List[str],
        )

        output = await invoker(input := [1, 2])

        self.assertEqual(output, expected_output)

        aws_lambda_client.invoke.assert_awaited_once_with(
            FunctionName=function_name,
            Payload=json.dumps(input).encode(),
        )
