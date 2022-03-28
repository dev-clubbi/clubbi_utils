from typing import Callable, Optional, AsyncContextManager, AsyncIterator

from pydantic import BaseSettings
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

SessionMaker = Callable[[], AsyncContextManager[AsyncSession]]

from typing import Any, Callable, Coroutine, TypeVar

F = TypeVar(
    "F",
    bound=Callable[..., Coroutine[Any, Any, Any]],
)
T = TypeVar("T")


class SqlAlchemyConfig(BaseSettings):
    user: str
    database: str
    host: str
    port: int
    password: str
    pool_min_size: int = 5
    pool_max_size: int = 10
    pool_timeout: int = 30  # default query timeout
    pool_recycle: int = -1
    echo: bool = False
    driver_name: str

    class Config:
        env_prefix = "sqlalchemy_"

    def to_sqlalchemy_uri(self) -> URL:
        return URL.create(
            drivername=self.driver_name,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )

    def create_engine(self) -> AsyncEngine:
        """engine is meant to be used alongside Sqlalchemy-Core"""

        engine = create_async_engine(
            self.to_sqlalchemy_uri(),
            echo=self.echo,
            pool_size=self.pool_min_size,
            max_overflow=self.pool_max_size - self.pool_min_size,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
        )

        return engine

    async def init_engine(self) -> AsyncIterator[AsyncEngine]:
        """this method is meant to be used alongside sqllachemy-core sand frameworks such as:
        - aiohttp
        - FastAPI,
        - dependency-injector
        """
        engine = self.create_engine()
        try:
            yield engine
        finally:
            await engine.dispose()

    async def init_session_maker(self) -> AsyncIterator[SessionMaker]:
        """this method is meant to be used alongside sqlalchemy-orm and frameworks such as:
        - aiohttp
        - FastAPI,
        - dependency-injector
        """
        engine = self.create_engine()
        try:
            yield create_sqlalchemy_session_maker(engine=engine)
        finally:
            await engine.dispose()

    def with_engine(self, f: F) -> Callable[..., Coroutine[Any, Any, T]]:
        """Mostly useful along side lambda and sqlalchemy-core"""

        async def wrapper(*args: Any, **kwargs: dict) -> Any:
            engine = self.create_engine()
            try:
                r = await f(engine, *args, **kwargs)
                return r
            finally:
                await engine.dispose()

        return wrapper

    def with_session_maker(self, f: F) -> Callable[..., Coroutine[Any, Any, T]]:
        """Mostly useful along side lambda and sqlalchemy-orm"""

        async def wrapper(*args: Any, **kwargs: dict) -> Any:
            engine = self.create_engine()
            session_maker = create_sqlalchemy_session_maker(engine=engine)
            try:
                r = await f(session_maker, *args, **kwargs)
                return r
            finally:
                await engine.dispose()

        return wrapper


def create_sqlalchemy_session_maker(
    *, engine: Optional[AsyncEngine], config: Optional[SqlAlchemyConfig] = None, expire_on_commit: bool = False
) -> SessionMaker:
    assert not (engine is not None and config is not None)
    if config:
        engine = config.create_engine()
    elif engine is None:
        engine = SqlAlchemyConfig().create_engine()
    return sessionmaker(engine, expire_on_commit=expire_on_commit, class_=AsyncSession)
