from typing import Union, Any, Callable, Set

from pydantic import BaseModel

try:
    import orjson
    from orjson import dumps as _dumps, loads as _loads, OPT_INDENT_2, OPT_SORT_KEYS, OPT_NON_STR_KEYS
    from decimal import Decimal

    def _serialize_default(obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, BaseModel):
            return obj.dict()
        if isinstance(obj, Set):
            return list(obj)
        raise TypeError

    def dumps(
        data: Any, /, pretty: bool = False, sort_keys: bool = False, non_str_keys: bool = True, default: Callable[[Any], Any] = _serialize_default
    ) -> str:
        option = 0
        if pretty:
            option |= OPT_INDENT_2
        if sort_keys:
            option |= OPT_SORT_KEYS
        if non_str_keys:
            option |= OPT_NON_STR_KEYS

        return _dumps(data, option=option, default=default).decode()

    def loads(data: str) -> Union[str, dict, list, int, float]:
        return _loads(data)

except ImportError:
    from json import dumps as default_dumps, loads as default_loads
    from pydantic.json import pydantic_encoder
    from decimal import Decimal

    def _default(obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        return pydantic_encoder(obj)

    def dumps(
        data: Any, /, pretty: bool = False, sort_keys: bool = False, non_str_keys: bool = True, default: Callable[[Any], Any] = _default
    ) -> str:
        return default_dumps(data, default=default, sort_keys=sort_keys, indent=2 if pretty else None)

    def loads(data: str) -> Union[str, dict, list, int, float]:
        return default_loads(data)
