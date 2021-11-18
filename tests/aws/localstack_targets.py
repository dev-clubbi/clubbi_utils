from aiobotocore import AioSession
from aiobotocore.client import AioBaseClient


class LocalStack:
    SNS_TARGET = 'http://localhost:4566'
    SES_TARGET = 'http://localhost:4566'


def create_test_client(session: AioSession, service_name: str) -> AioBaseClient:
    return session.create_client(service_name, region_name='us-east-1',
                                 aws_access_key_id='foo', aws_secret_access_key='bar',
                                 endpoint_url=LocalStack.SES_TARGET
                                 )
