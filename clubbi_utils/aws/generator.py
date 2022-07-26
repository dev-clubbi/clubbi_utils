from typing import AsyncGenerator, Optional

from aiobotocore.client import AioBaseClient

from clubbi_utils.aws.decorator import _get_session, build_aws_config


async def aws_resource_context(
        name: str,
        region_name: Optional[str] = None,
        read_timeout: Optional[int] = None,
        max_retry_attempts: Optional[int] = None,
) -> AsyncGenerator[AioBaseClient, None]:
    """
    This function is quite useful when used alongside dependency-injector library
    :param name:
    :param region_name:
    :param read_timeout:
    :param max_retry_attempts:
    :return:
    """
    session = _get_session()
    config, session_kwargs = build_aws_config(
        region_name,
        read_timeout,
        max_retry_attempts,
    )
    async with session.create_client(name, config=config, **session_kwargs) as client:
        yield client
