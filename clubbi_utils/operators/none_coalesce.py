from typing import TypeVar, Optional

T = TypeVar("T")


def none_coalesce(*args: Optional[T], default: T) -> T:
    return next((a for a in args if a is not None), default)
