from typing import Protocol, TypeVar

IN = TypeVar("IN", contravariant=True)
OUT = TypeVar("OUT", covariant=True)


class AsyncCallable(Protocol[IN, OUT]):
    async def __call__(self, input_: IN) -> OUT:
        ...
