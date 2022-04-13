from typing import List
from clubbi_utils.common.batched_gather import batched_gather
import asyncio
import time
from unittest import IsolatedAsyncioTestCase


async def sleep_and_return(delay: float) -> float:
    await asyncio.sleep(delay)
    return delay


async def run_and_join_results(collection: List[float], number_of_workesrs: int) -> List[float]:
    return sum([b async for b in batched_gather(sleep_and_return, collection, number_of_workesrs)], [])


class TestBatchedGather(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._collection = [0.125] * 6
        return super().setUp()

    async def test_batched_gather(self):
        output = await run_and_join_results(self._collection, len(self._collection) // 2)
        self.assertEqual(output, self._collection)

    async def test_batched_gather_speed(self):
        start = time.time()
        await run_and_join_results(self._collection, len(self._collection) // 2)
        time_took_half = time.time() - start

        start = time.time()
        await run_and_join_results(self._collection, len(self._collection))
        time_took_full = time.time() - start

        self.assertTrue(time_took_half >= time_took_full)
