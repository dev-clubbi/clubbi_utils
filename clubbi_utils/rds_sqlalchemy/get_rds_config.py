from asyncio import gather

from aiobotocore.client import AioBaseClient
from clubbi_utils.aws.decorator import with_aws_client
from clubbi_utils.sqlalchemy.connector import SqlAlchemyConfig


@with_aws_client("secretsmanager")
@with_aws_client("rds")
async def load_rds_sqlalchemy_config(
        rds: AioBaseClient,
        secretsmanager: AioBaseClient,
        rds_instance_id: str,
        database_name: str,
        user_name: str,
        password_secret_id: str,
        driver_name: str,
) -> SqlAlchemyConfig:
    database_describe, password_data = await gather(
        rds.describe_db_instances(DBInstanceIdentifier=rds_instance_id),
        secretsmanager.get_secret_value(
            SecretId=password_secret_id,
        ),
    )

    password = password_data["SecretString"]
    endpoint = database_describe["DBInstances"][0]["Endpoint"]

    return SqlAlchemyConfig(
        database=database_name,
        user=user_name,
        password=password,
        host=endpoint["Address"],
        port=endpoint["Port"],
        driver_name=driver_name,
    )
