from typing import Tuple, Any, Generator

import pytest


from tests.json.fixtures import dumps_fixture, loads_to_compare


@pytest.fixture
def json_fixture() -> Generator[Tuple[Any, Any], None, None]:
    import builtins

    real_import = builtins.__import__

    def _import(name, _globals, _locals, fromlist, level):
        if name == 'orjson':
            raise ImportError
        return real_import(name, _globals, _locals, fromlist, level)

    builtins.__import__ = _import  # type: ignore

    from clubbi_utils import json
    from importlib import reload
    reload(json)

    yield json.loads, json.dumps
    builtins.__import__ = real_import  # type: ignore


def test_dumps_loads(json_fixture):
    loads, dumps = json_fixture
    data = loads(dumps(dumps_fixture))
    assert loads_to_compare == data
