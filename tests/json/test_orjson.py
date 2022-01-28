from typing import Tuple, Any, Generator

import pytest

from tests.json.fixtures import dumps_fixture, loads_to_compare


@pytest.fixture
def json_fixture() -> Generator[Tuple[Any, Any], None, None]:

    from clubbi_utils import json
    from importlib import reload
    reload(json)
    yield json.loads, json.dumps




def test_dumps_loads(json_fixture):
    loads, dumps = json_fixture
    data = loads(dumps(dumps_fixture, pretty=True, sort_keys = True))
    assert loads_to_compare == data
