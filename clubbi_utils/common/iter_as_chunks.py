from typing import Iterable, List, TypeVar
import itertools


T = TypeVar("T")


def iter_as_chunks(iterable: Iterable[T], n: int) -> Iterable[List[T]]:
    it = iter(iterable)
    while chunk := list(itertools.islice(it, n)):
        yield chunk
