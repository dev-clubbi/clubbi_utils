import asyncio
from clubbi_utils.common.iter_as_chunks import iter_as_chunks
from typing import AsyncIterator, Awaitable, Callable, Iterable, List, TypeVar, overload, Literal, Union

OUTPUT = TypeVar("OUTPUT")
INPUT = TypeVar("INPUT")


@overload
def batched_gather(
    f: Callable[[INPUT], Awaitable[OUTPUT]],
    collection: Iterable[INPUT],
    number_of_workers: int,
    return_exceptions: Literal[True],
) -> AsyncIterator[List[Union[Exception, OUTPUT]]]:
    pass


@overload
def batched_gather(
    f: Callable[[INPUT], Awaitable[OUTPUT]],
    collection: Iterable[INPUT],
    number_of_workers: int,
    return_exceptions: bool = False,
) -> AsyncIterator[List[OUTPUT]]:
    pass


async def batched_gather(  # type: ignore[misc]
    f: Callable[[INPUT], Awaitable[OUTPUT]],
    collection: Iterable[INPUT],
    number_of_workers: int,
    return_exceptions: bool = False,
) -> AsyncIterator[List[Union[Exception, OUTPUT]]]:
    for batch in iter_as_chunks(collection, number_of_workers):
        coros = (f(input_) for input_ in batch)
        chunk = list(await asyncio.gather(*coros, return_exceptions=return_exceptions))
        yield chunk
