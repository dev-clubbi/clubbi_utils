from functools import lru_cache, wraps
from os import getenv
from typing import Optional, Any, Callable

from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig
from aiobotocore.session import AioSession
from aiobotocore.session import get_session
from pydantic import BaseSettings

from clubbi_utils.aws.local_mocks.s3_object_storage_local_mock import S3ObjectStorageLocalMock
from clubbi_utils.aws.s3_object_storage import S3ObjectStorage


@lru_cache
def _get_session() -> AioSession:
    return get_session()


class AioBotocoreSettings(BaseSettings):
    boto_region_name: Optional[str] = None
    boto_read_timeout: int = 60
    boto_max_retry_attempts: int = 5


def with_aws_client(
    name: str,
    region_name: Optional[str] = None,
    read_timeout: Optional[int] = None,
    max_retry_attempts: Optional[int] = None,
) -> Callable:
    def wrap(f):
        async def wrapper(*args, **kwargs):
            settings_kwargs = dict(
                boto_region_name=region_name,
                boto_read_timeout=read_timeout,
                boto_max_retry_attempts=max_retry_attempts,
            )
            settings_kwargs_filtered = {k: v for k, v in settings_kwargs.items() if v is not None}
            settings = AioBotocoreSettings(**settings_kwargs_filtered)

            session = _get_session()
            config = AioConfig(
                read_timeout=settings.boto_read_timeout,
                retries=dict(max_attempts=settings.boto_max_retry_attempts),
            )

            session_kwargs = dict(region_name=settings.boto_region_name) if settings.boto_region_name != None else {}
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
    env: Optional[str] = None,
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
