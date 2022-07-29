from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine

from clubbi_utils.sqlalchemy.connector import SqlAlchemyConfig, SessionMaker, create_sqlalchemy_session_maker


class PostgresConfig(SqlAlchemyConfig):
    port: int = 5432
    driver_name: str = "postgresql+asyncpg"

    class Config:
        env_prefix = "postgres_"


def create_postgres_session_maker(
    *, engine: Optional[AsyncEngine] = None, config: Optional[PostgresConfig] = None, expire_on_commit: bool = False
) -> SessionMaker:
    if engine is None and config is None:
        config = PostgresConfig()
    return create_sqlalchemy_session_maker(engine=engine, config=config, expire_on_commit=expire_on_commit)
