import asyncio
from typing import Any, Callable, TypeVar, Coroutine

from clubbi_utils.common.typing.lambda_context import LambdaContext

T = TypeVar('T')

LambdaHandler = Callable[[], Any]


def async_lambda(f: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    def handle(event_data: Any, context: LambdaContext) -> T:
        return asyncio.run(f(event_data, context))

    return handle


def async_lambda_no_input(f: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    def handle(_event_data: Any, _context: Any) -> T:
        return asyncio.run(f())

    return handle
