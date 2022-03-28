from typing import Optional

from aiomysql.sa import Engine, create_engine
from pydantic import BaseSettings


class MysqlConfig(BaseSettings):
    mysql_user: str
    mysql_database: str
    mysql_host: str
    mysql_port: int
    mysql_password: str
    mysql_pool_min_size: int = 1
    mysql_pool_max_size: int = 10


async def create_mysql_engine(config: Optional[MysqlConfig] = None) -> Engine:
    if config is None:
        config = MysqlConfig()
    return await create_engine(
        db=config.mysql_database,
        host=config.mysql_host,
        port=config.mysql_port,
        user=config.mysql_user,
        password=config.mysql_password,
        sql_mode="TRADITIONAL",
        minsize=config.mysql_pool_min_size,
        maxsize=config.mysql_pool_max_size,
        autocommit=True,
    )
