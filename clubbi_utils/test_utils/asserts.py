from dataclasses import asdict
from typing import Any, Optional

from pydantic import BaseModel


def assert_dataclasses_equal(left: Any, right: Any, msg: Optional[str] = None) -> None:
    assert asdict(left) == asdict(right), msg


def assert_basemodel_equal(left: BaseModel, right: BaseModel, msg: Optional[str] = None) -> None:
    assert left.dict(exclude_none=True) == right.dict(exclude_none=True), msg
