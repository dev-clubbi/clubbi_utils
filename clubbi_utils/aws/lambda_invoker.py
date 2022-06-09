from asyncio import StreamReader
from dataclasses import dataclass
from typing import Dict, Generic, Any, Type
from aiobotocore.client import AioBaseClient
from clubbi_utils.async_callable import AsyncCallable, IN, OUT
from pydantic import parse_obj_as, parse_raw_as
from pydantic.error_wrappers import ValidationError

from clubbi_utils import json


@dataclass
class LambdaRaisedAnExceptionError(RuntimeError):
    function_name: str
    payload: Dict

    def __str__(self) -> str:
        return f"Lambda '{self.function_name}' raised the following exception: {json.dumps(self.payload, pretty=True)}"


@dataclass
class InvalidInputType(ValueError):
    expected: Type

    def __str__(self) -> str:
        return f"Invalid input type, expected: {self.expected}"


@dataclass
class FailedToParseOutputError(RuntimeError):
    function_name: str
    output: Any

    def __str__(self) -> str:
        return f"AwsLambdaInvoker '{self.function_name}' couldn't parse the following output: {json.dumps(self.output, pretty=True)}"


class AwsLambdaInvoker(AsyncCallable, Generic[IN, OUT]):
    """Generic lambda invoker class, with an input type `IN` and output type `OUT` passed as parameters, the input type is
    checked at runtime and the output type is parsed if `OUT` is a dataclass, or is a subclass of `pydantic.BaseModel`.

    Args:
        aws_lambda_client (AioBaseClient): aiobotocore base client
        function_name (str): lambda function name
        input_type (Type[IN]): Input type to be checked at runtime
        output_type (Type[OUT]): Output type to be parsed
    """

    def __init__(
        self,
        aws_lambda_client: AioBaseClient,
        function_name: str,
        input_type: Type[IN],
        output_type: Type[OUT],
    ):
        self._client = aws_lambda_client
        self._function_name = function_name
        self._input_type = input_type
        self._output_type = output_type

    def __check_for_errors(self, payload: Dict) -> None:
        if "errorMessage" in payload:
            raise LambdaRaisedAnExceptionError(
                function_name=self._function_name,
                payload=payload,
            )

    def __parse_response_body(self, decoded_body: Any) -> OUT:
        try:
            return parse_obj_as(self._output_type, decoded_body)
        except ValidationError as e:
            raise FailedToParseOutputError(
                function_name=self._function_name,
                output=decoded_body,
            ) from e

    def __check_input_type(self, payload_str: str) -> None:
        try:
            parse_raw_as(self._input_type, payload_str)
        except ValidationError as e:
            raise InvalidInputType(expected=self._input_type) from e
    
    async def __call__(self, input_: IN) -> OUT:
        payload_str = json.dumps(input_)
        self.__check_input_type(payload_str)
        payload_bytes = payload_str.encode()
        lambda_response = await self._client.invoke(
            FunctionName=self._function_name,
            Payload=payload_bytes,
        )

        payload_reader: StreamReader = lambda_response["Payload"]
        raw_body = await payload_reader.read()
        decoded_body = json.loads(raw_body.decode())

        if isinstance(decoded_body, dict):
            self.__check_for_errors(decoded_body)
        
        return self.__parse_response_body(decoded_body)
