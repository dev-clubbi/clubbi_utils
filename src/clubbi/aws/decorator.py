from collections import Callable
from functools import lru_cache
from typing import Optional

import aiobotocore
from aiobotocore import AioSession


@lru_cache
def _get_session() -> AioSession:
    return aiobotocore.get_session()


def with_aws_client(name: str, region_name: Optional[str] = None) -> Callable:
    def wrap(f):
        async def wrapper(*args, **kwargs):
            session = _get_session()

            session_kwargs = dict(region_name=region_name) if region_name != None else {}
            async with session.create_client(name, **session_kwargs) as client:
                return await f(client, *args, **kwargs)

        return wrapper

    return wrap