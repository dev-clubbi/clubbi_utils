import asyncio
import logging
import sys
from logging.config import fileConfig
from os import getenv
from typing import cast, Any, Optional

from alembic import context

from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData

from clubbi_utils.logging import logger
from clubbi_utils.rds_sqlalchemy.get_rds_config import load_rds_sqlalchemy_config

try:
    config = context.config
    assert isinstance(config.config_file_name, str)
    fileConfig(config.config_file_name)
except AttributeError:
    logging.exception(dict(message='run using alembic CLI'))
    exit(1)


async def get_sqlalchemy_url(config: Config) -> Optional[str]:
    my_env = getenv('ALEMBIC_RDS_ENVIRONMENT', None)

    if my_env:
        driver = config.get_main_option('sql_driver')
        rds_data = config.get_section(f'rds.{my_env}')
        assert rds_data
        pg_config = await load_rds_sqlalchemy_config(
            rds_instance_id=rds_data['instance_id'],
            database_name=rds_data['database_name'],
            user_name=rds_data['user_name'],
            password_secret_id=rds_data['password_secret_id'],
            driver_name=driver,
        )
        if sys.stdin.isatty():
            in_ = input(f"""\nAre changing [\033[1m{my_env}\033[0m] database?\nconfirm typing yes:""")
            if 'yes' != in_:
                logger.warn("skipping because you did not confirm it with `yes`...")
                return None
        url = str(pg_config.to_sqlalchemy_uri())
    else:
        url = getenv('SQLALCHEMY_URI', config.get_main_option("sqlalchemy.url") or '')

    return url


def run_alembic_env(target_metadata: MetaData) -> None:
    async def run_migrations_offline():
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.

        """

        url = await get_sqlalchemy_url(config)
        if url is None:
            return
        config.set_main_option('sqlalchemy.url', url)
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={
                "paramstyle": "named"
            },
        )

        with context.begin_transaction():
            context.run_migrations()

    async def run_migrations_online():
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        url = await get_sqlalchemy_url(config)
        if url is None:
            return

        engine = create_async_engine(url)

        def do_migrations(connection_):
            options = cast(dict[str, Any], config.get_section(config.config_ini_section))
            context.configure(connection=connection_, target_metadata=target_metadata, **options)

            with context.begin_transaction():
                context.run_migrations()

        async with engine.connect() as connection:
            await connection.run_sync(do_migrations)

    if context.is_offline_mode():
        asyncio.run(run_migrations_offline())
    else:
        asyncio.run(run_migrations_online())
