import asyncio
from clubbi_utils.common.iter_as_chunks import iter_as_chunks
from typing import AsyncGenerator, Awaitable, Callable, Iterable, List, TypeVar

OUTPUT = TypeVar("OUTPUT")
INPUT = TypeVar("INPUT")


async def batched_gather(
    f: Callable[[INPUT], Awaitable[OUTPUT]],
    collection: Iterable[INPUT],
    number_of_workers: int,
) -> AsyncGenerator[List[OUTPUT], None]:
    for batch in iter_as_chunks(collection, number_of_workers):
        yield list(await asyncio.gather(*(f(input_) for input_ in batch)))
