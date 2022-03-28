from typing import TypeVar, Callable, Any, Coroutine

from clubbi_utils.sqlalchemy.connector import SqlAlchemyConfig

F = TypeVar(
    "F",
    bound=Callable[..., Coroutine[Any, Any, Any]],
)
T = TypeVar("T")


def with_sqlalchemy_engine(f: F) -> Callable[..., Coroutine[Any, Any, T]]:
    # config: Optional[MysqlConfig] = None
    # def _dec(f: F) -> Callable[..., Coroutine[Any, Any, T]]:
    async def wrapper(*args: Any, **kwargs: dict) -> Any:
        db = SqlAlchemyConfig().create_engine()
        try:
            r = await f(db, *args, **kwargs)
            return r
        finally:
            await db.dispose()

    return wrapper
