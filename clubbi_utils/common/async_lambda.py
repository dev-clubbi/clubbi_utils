import asyncio
from functools import wraps
from typing import Any, Callable, TypeVar, Coroutine, Optional, Awaitable

from clubbi_utils.common.typing.lambda_context import LambdaContext

T = TypeVar('T')

LambdaHandler = Callable[[], Any]


def async_lambda(
        f: Optional[Callable[..., Coroutine[Any, Any, T]]] = None,
        *,
        init: Optional[Callable[[], Awaitable]] = None,
) -> Callable[..., T]:
    def wrapper(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
        if init is not None:

            @wraps(func)
            def handle(event_data: Any, context: LambdaContext) -> T:
                async def _f(event_data_: Any, context_: LambdaContext) -> T:
                    await init()  # type: ignore
                    return await func(event_data_, context_)

                return asyncio.run(_f(event_data, context))
        else:
            @wraps(func)
            def handle(event_data: Any, context: LambdaContext) -> T:
                return asyncio.run(func(event_data, context))
        return handle

    if f is None:
        return wrapper  # type: ignore

    return wrapper(f)


def async_lambda_no_input(f: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    def handle(_event_data: Any, _context: Any) -> T:
        return asyncio.run(f())

    return handle
