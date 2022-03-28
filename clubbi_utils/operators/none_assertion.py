from typing import TypeVar, Optional


class ValueIsNoneError(ValueError):
    pass


T = TypeVar("T")


def none_assertion(v: Optional[T]) -> T:
    if v is None:
        raise ValueIsNoneError()
    return v
