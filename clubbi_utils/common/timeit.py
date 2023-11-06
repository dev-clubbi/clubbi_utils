import time
from inspect import iscoroutinefunction
from typing import Callable
from clubbi_utils.json_logging import jlogger


def _log(f: Callable, begin: float, end: float) -> None:
    meta = dict(
        qualname=f.__qualname__,
        module=f.__module__,
    )
    jlogger.info(f.__name__, "time_elapsed", duration=end - begin, meta=meta)


def with_timeit(f: Callable) -> Callable:
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
        return async_wrapper
    else:
        return wrapper
