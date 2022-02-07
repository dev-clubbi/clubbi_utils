import abc
from typing import Generic, TypeVar

T = TypeVar("T")


class AsyncSender(abc.ABC, Generic[T]):
    @abc.abstractclassmethod
    async def send(self, data: T):
        pass


AsyncSenderStr = AsyncSender[str]
