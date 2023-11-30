from dataclasses import dataclass
from typing import Any, Optional, TypedDict


class ErrorUnit(TypedDict):
    identifier: Optional[str]
    msg: str
    loc: str
    type: str


@dataclass
class ClubbiValidationError(Exception):
    errors: list[ErrorUnit]
    model: str

    def dict(self) -> dict[str, Any]:
        return dict(
            errors=self.errors,
            model=self.model,
        )
