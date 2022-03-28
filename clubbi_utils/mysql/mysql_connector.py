from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine

from clubbi_utils.sqlalchemy.connector import SqlAlchemyConfig, SessionMaker, create_sqlalchemy_session_maker


class MysqlConfig(SqlAlchemyConfig):
    port: int = 3306
    pool_recycle: int = 3600
    driver_name: str = "mysql+asyncmy"

    class Config:
        env_prefix = "mysql_"


def create_mysql_session_maker(
    *, engine: Optional[AsyncEngine], config: Optional[MysqlConfig] = None, expire_on_commit: bool = False
) -> SessionMaker:
    if engine is None and config is None:
        config = MysqlConfig()
    return create_sqlalchemy_session_maker(engine=engine, config=config, expire_on_commit=expire_on_commit)
