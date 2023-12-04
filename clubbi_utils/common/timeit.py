import time
from inspect import iscoroutinefunction
from typing import Callable, TypeVar, cast
from clubbi_utils.json_logging import jlogger


def _log(f: Callable, begin: float, end: float) -> None:
    meta = dict(
        qualname=f.__qualname__,
        module=f.__module__,
    )
    jlogger.info(f.__name__, "time_elapsed", duration=end - begin, meta=meta)


FUNCTION_TYPE = TypeVar("FUNCTION_TYPE", bound=Callable)


def with_timeit(f: FUNCTION_TYPE) -> FUNCTION_TYPE:
    def wrapper(*args, **kwargs):
        begin = time.time()
        r = f(*args, **kwargs)
        end = time.time()
        _log(f, begin, end)
        return r

    async def async_wrapper(*args, **kwargs):
        begin = time.time()
        r = await f(*args, **kwargs)
        end = time.time()
        _log(f, begin, end)
        return r

    if iscoroutinefunction(f):
        return cast(FUNCTION_TYPE, async_wrapper)
    else:
        return cast(FUNCTION_TYPE, wrapper)
