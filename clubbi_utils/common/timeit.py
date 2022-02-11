import time
from inspect import iscoroutinefunction, getframeinfo, getmembers

from clubbi_utils.logger import logger


def timeit(f):
    meta = dict(
        qualname=f.__qualname__,
        __module__=f.__module__,
    )

    def wrapper(*args, **kwargs):
        begin = time.time()
        r = f(*args, **kwargs)
        end = time.time()
        logger.info(dict(name=f.__name__, duration=end - begin, meta=meta))
        return r

    async def async_wrapper(*args, **kwargs):
        begin = time.time()
        r = await f(*args, **kwargs)
        end = time.time()
        logger.info(dict(name=f.__name__, duration=end - begin, meta=meta))
        return r

    if iscoroutinefunction(f):
        return async_wrapper
    else:
        return wrapper
