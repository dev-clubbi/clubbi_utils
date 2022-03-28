from typing import Any, Callable, Coroutine, TypeVar

from clubbi_utils.logging import logger
from clubbi_utils.mysql.mysql_connector import MysqlConfig

F = TypeVar(
    "F",
    bound=Callable[..., Coroutine[Any, Any, Any]],
)
T = TypeVar("T")


def with_sql_engine(f: F) -> Callable[..., Coroutine[Any, Any, T]]:
    """this method is deprecated"""
    logger.warn("with_sql_egine is deprecated, use @MysqlConfig().with_engine()")
    return MysqlConfig().with_engine(f)
