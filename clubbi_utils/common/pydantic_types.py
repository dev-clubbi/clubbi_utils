from datetime import date, datetime
from typing import Any, Callable, Union


class BrDate(date):
    @classmethod
    def __get_validators__(cls) -> Callable[[Any], date]:
        yield cls._validate

    @classmethod
    def _validate(cls, value: Any) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, "%d/%m/%Y").date()
        else:
            raise ValueError(f"Unrecognized type {value}")


BrCompatibleDate = Union[BrDate, date]
