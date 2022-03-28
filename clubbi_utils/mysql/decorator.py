from typing import Any, Callable, Coroutine, TypeVar

from clubbi_utils.mysql.mysql_connector import create_mysql_engine

F = TypeVar(
    "F",
    bound=Callable[..., Coroutine[Any, Any, Any]],
)
T = TypeVar("T")


def with_sql_engine(f: F) -> Callable[..., Coroutine[Any, Any, T]]:
    # config: Optional[MysqlConfig] = None
    # def _dec(f: F) -> Callable[..., Coroutine[Any, Any, T]]:
    async def wrapper(*args: Any, **kwargs: dict) -> Any:
        db = await create_mysql_engine()
        try:
            r = await f(db, *args, **kwargs)
            return r
        finally:
            db.close()
            await db.wait_closed()

    return wrapper
