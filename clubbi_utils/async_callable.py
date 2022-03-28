from typing import TypeVar, Generic

IN = TypeVar("IN")
OUT = TypeVar("OUT")


class AsyncCallable(Generic[IN, OUT]):
    async def __call__(self, input_: IN) -> OUT:
        pass
