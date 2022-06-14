from typing import TypeVar, Union


class Undefined(object):
    def __bool__(self):
        return False

    def __eq__(self, other):
        return type(self) == type(other)

    def __copy__(self):
        return self

    def __deepcopy__(self, _):
        return self

    def __hash__(self):
        return hash(None) + 1


UNDEFINED = Undefined()

T = TypeVar("T")

Undefinable = Union[T, Undefined]
