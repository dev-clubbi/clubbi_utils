from functools import lru_cache, wraps
from os import getenv
from typing import Optional, Any, Callable

import aiobotocore
from aiobotocore import AioSession

from clubbi_utils.aws.local_mocks.s3_object_storage_local_mock import S3ObjectStorageLocalMock
from clubbi_utils.aws.s3_object_storage import S3ObjectStorage
from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig
from pydantic import BaseSettings
from clubbi_utils.operators import none_coalesce


@lru_cache
def _get_session() -> AioSession:
    return aiobotocore.get_session()

class AioBotocoreSettings(BaseSettings):
    boto_region_name: Optional[str] = None
    boto_read_timeout: int = 60
    boto_max_retry_attempts: int = 5

def with_aws_client(
    name: str,
    region_name: Optional[str]=None,
    read_timeout:Optional[int]=None,
    max_retry_attempts:Optional[int]=None,
) -> Callable:
    def wrap(f):
        async def wrapper(*args, **kwargs):
            _settings = AioBotocoreSettings()
            region_name = none_coalesce(region_name, default=_settings.boto_region_name)
            max_retry_attempts = none_coalesce(max_retry_attempts, default=_settings.boto_max_retry_attempts)
            read_timeout = none_coalesce(read_timeout, default=_settings.boto_read_timeout)
            
            session = _get_session()
            config = AioConfig(
                read_timeout=read_timeout,
                retries=dict(max_attempts=max_retry_attempts),
            )

            session_kwargs = dict(region_name=region_name) if region_name != None else {}
            async with session.create_client(name, config=config, **session_kwargs) as client:
                return await f(client, *args, **kwargs)

        return wrapper

    return wrap

@lru_cache
def _get_cached_local_mock(
    bucket_name: str,
    key_prefix: str,
) -> S3ObjectStorageLocalMock:
    return S3ObjectStorageLocalMock(
        name=bucket_name,
        key_prefix=key_prefix,
    )


def with_object_storage(
    bucket_name: str,
    key_prefix: str = "",
    region_name: str = "us-east-1",
    env: str = None,
) -> Callable:
    """Injects a positional parameter which is a S3ObjectStorage if env is staging or production
    otherwise returns a cached S3ObjectStorageLocalMock."""
    env = env or getenv("ENVIRONMENT")

    def prod_staging_decorator(f: Callable) -> Callable:
        @wraps(f)
        @with_aws_client("s3", region_name=region_name)
        async def wrapper(client: AioBaseClient, *args: Any, **kwargs: Any) -> Any:
            object_storage = S3ObjectStorage(
                client=client,
                bucket=bucket_name,
                key_prefix=key_prefix,
            )
            return await f(object_storage, *args, **kwargs)
        return wrapper
    
    def local_decorator(f: Callable) -> Callable:
        @wraps(f)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            object_storage = _get_cached_local_mock(bucket_name, key_prefix)
            return await f(object_storage, *args, **kwargs)
        return wrapper

    if env in {"production", "staging"}:
         return prod_staging_decorator
    return local_decorator
