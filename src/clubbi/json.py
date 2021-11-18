import json
from dataclasses import is_dataclass
from typing import Union, Any, Optional

from pydantic.json import pydantic_encoder


def dumps(data: Any, indent: Optional[int] = 2) -> str:
    return json.dumps(data, default=pydantic_encoder, indent=indent, sort_keys=True)


def loads(data: str) -> Union[str, dict, list, int, float]:
    return json.loads(data)
