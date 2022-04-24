from typing import List, Optional, Union
from clubbi_utils.common.batched_gather import batched_gather
import asyncio
import time
from unittest import IsolatedAsyncioTestCase
from itertools import zip_longest


async def sleep_and_return(delay: Optional[float]) -> float:
    if delay is None:
        raise RuntimeError()
    await asyncio.sleep(delay)
    return delay


async def run_and_join_results(collection: List[float], number_of_workers: int) -> List[float]:
    return sum([b async for b in batched_gather(sleep_and_return, collection, number_of_workers)], [])


async def run_and_join_results_with_exception(
    collection: List[Optional[float]],
    number_of_workers: int,
) -> List[Union[float, Exception]]:
    return sum([b async for b in batched_gather(sleep_and_return, collection, number_of_workers, True)], [])


class TestBatchedGather(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._collection = [0.125] * 6
        self._err_collection = [0.1 if i % 2 else None for i in range(5)]
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

    async def test_batched_gather_return_exception(self):
        output = await run_and_join_results_with_exception(self._err_collection, len(self._err_collection) // 2)
        for f, o in zip_longest(self._err_collection, output):
            if f is not None:
                self.assertEqual(f, o)
            else:
                self.assertTrue(isinstance(o, RuntimeError))
