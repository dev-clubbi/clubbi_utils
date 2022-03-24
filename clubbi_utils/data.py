from collections import defaultdict
from typing import Iterable, TypeVar, Dict, List, Callable, Hashable

T = TypeVar("T")
K = TypeVar("K", bound=Hashable, covariant=True)


def group_by(collection: Iterable[T], key: Callable[[T], K]) -> Dict[K, List[T]]:
    res: Dict[K, List[T]] = defaultdict(list)
    for value in collection:
        res[key(value)].append(value)
    return res
