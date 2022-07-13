from collections.abc import Iterable
from typing import AsyncContextManager, Optional, Union

from sqlalchemy import select, BigInteger, values, column, literal
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection
from sqlalchemy.sql.functions import func

_lock = func.pg_advisory_lock
_unlock = func.pg_advisory_unlock


class _PostgresAdvisoryLockManager:

    def __init__(self, engine: AsyncEngine, key: Union[int, Iterable[int]]):
        self._engine = engine
        self._conn: Optional[AsyncConnection] = None

        if isinstance(key, (list, tuple, set)):
            subquery = values(column("k", BigInteger), name="t").data(
                [(literal(key_, BigInteger),) for key_ in set(key)]
            )
            self._lock = select(_lock(subquery.c.k)).select_from(subquery)
            self._unlock = select(_unlock(subquery.c.k)).select_from(subquery)
        else:
            key_ = literal(key, BigInteger)
            self._lock = select(_lock(key_))
            self._unlock = select(_unlock(key_))

    async def __aenter__(self) -> None:
        self._conn = await self._engine.connect()
        await self._conn.execute(self._lock)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            await self._conn.execute(self._unlock)
            await self._conn.close()


class PostgresAdvisoryLocker:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    def acquire(self, key: Union[int, Iterable[int]]) -> AsyncContextManager[None]:
        return _PostgresAdvisoryLockManager(self._engine, key)
