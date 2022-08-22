from datetime import datetime
from typing import Union, List, Type, TypeVar, TypedDict, overload
from aiobotocore.client import AioBaseClient
from pydantic import parse_raw_as


class GetSecretValueResponse(TypedDict):
    ARN: str
    Name: str
    VersionId: str
    SecretBinary: bytes
    SecretString: str
    VersionStages: List[str]
    CreatedDate: datetime


SECRET_TYPE = TypeVar("SECRET_TYPE")


@overload
async def get_ssm_secret(ssm_client: AioBaseClient, secret_name: str, secret_type: Type[SECRET_TYPE]) -> SECRET_TYPE:
    pass


@overload
async def get_ssm_secret(ssm_client: AioBaseClient, secret_name: str, secret_type: Type = str) -> str:
    pass


async def get_ssm_secret(
    ssm_client: AioBaseClient,
    secret_name: str,
    secret_type: Type = str,
) -> Union[str, SECRET_TYPE]:
    """Gets an AWS Secrets Manager value

    example:
    ```
    @with_aws_client("secretsmanager")
    async def main(ssm_client: AioBaseClient) -> None:
        my_secret_str = await get_ssm_secret(ssm_client, "my_secret_key")
        my_secret_dict = await get_ssm_secret(ssm_client, "my_secret_key_dict", Dict[str, Any])
        my_secret_base_model = await get_ssm_secret(ssm_client, "my_secret_base_model", MyBaseModel)

    ```

    Args:
        ssm_client (AioBaseClient): aiobotocore client
        secret_name (str): Secret key
        secret_type (Type, optional): Secret value output. Defaults to str.

    Returns:
        Union[str, SECRET_TYPE]: Secret value
    """
    res: GetSecretValueResponse = await ssm_client.get_secret_value(SecretId=secret_name)
    secret_string = res["SecretString"]
    if secret_type == str:
        return secret_string
    return parse_raw_as(secret_type, secret_string)
