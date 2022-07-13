import asyncio
from asyncio import gather
from collections import defaultdict
from random import randint
from unittest import IsolatedAsyncioTestCase

from clubbi_utils.postgres.advisory_locker import PostgresAdvisoryLocker
from clubbi_utils.postgres.postgres_connector import PostgresConfig


class TestPgLock(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self._engine = PostgresConfig(user='test', password='test', host='127.0.0.1', database='test').create_engine()
        self._locker = PostgresAdvisoryLocker(self._engine)

    async def asyncTearDown(self) -> None:
        await self._engine.dispose()

    async def test_concurrent_snippet_broke_without_lock(self):
        running_flag: dict[int, int] = defaultdict(lambda: False)

        async def run_(key: int) -> None:
            await asyncio.sleep(randint(25, 50) / 10000)
            assert running_flag[key] is False
            running_flag[key] = True
            await asyncio.sleep(randint(25, 50) / 10000)
            running_flag[key] = False

        with self.assertRaises(AssertionError):
            await gather(*(run_(x % 4) for x in range(100)))

    async def test_snippet_never_run_concurrently(self):
        running_flag: dict[int, int] = defaultdict(lambda: False)

        async def run_(key: int) -> None:
            async with self._locker.acquire(key):
                await asyncio.sleep(randint(25, 50) / 10000)
                assert running_flag[key] is False
                running_flag[key] = True
                await asyncio.sleep(randint(25, 50) / 10000)
                running_flag[key] = False

        await gather(*(run_(x % 4) for x in range(100)))

    async def test_group_lock(self):
        running_flag: dict[int, int] = defaultdict(lambda: False)

        async def run_(keys: tuple[int, ...]) -> None:
            async with self._locker.acquire(keys):
                await asyncio.sleep(randint(25, 50) / 10000)
                assert all(running_flag[key] is False for key in keys)
                for key in keys:
                    running_flag[key] = True
                await asyncio.sleep(randint(25, 50) / 10000)
                for key in keys:
                    running_flag[key] = False

        hundred_tuples_of_variable_sizes = (tuple(randint(0, 3) for _ in range(randint(1, 20))) for x in range(100))
        await gather(*(run_(keys) for keys in hundred_tuples_of_variable_sizes))
