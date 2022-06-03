import pytest
from io import StringIO
import logging
from clubbi_utils.json_logging import JsonLogger
from pydantic.dataclasses import dataclass
from pydantic import BaseModel

class ExampleBaseModel(BaseModel):
    n: int
    s: str

@dataclass
class ExamplePydanticDataclass:
    n: int
    s: str


@pytest.fixture
def mocked_stdout() -> StringIO:
    return StringIO()


@pytest.fixture
def mocked_logging(mocked_stdout: StringIO) -> logging.Logger:
    logger = logging.getLogger()
    logger.addHandler
    logger.addHandler(logging.StreamHandler(mocked_stdout))
    return logger


@pytest.fixture
def jlogger(mocked_logging: logging.Logger) -> JsonLogger:
    return JsonLogger(mocked_logging)


def test_json_logging(jlogger: JsonLogger, mocked_stdout: StringIO) -> None:
    jlogger.info("main", "test", input=1)
    assert mocked_stdout.getvalue().strip() == r'{"workflow":"main","message":"test","level":"INFO","input":1}'

def test_json_logging_with_base_model(jlogger: JsonLogger, mocked_stdout: StringIO) -> None:
    jlogger.info("main", "test", base_model=ExampleBaseModel(n=42, s="hello world"))
    assert mocked_stdout.getvalue().strip() == r'{"workflow":"main","message":"test","level":"INFO","base_model":{"n":42,"s":"hello world"}}'

def test_json_logging_with_pydantic_dataclass(jlogger: JsonLogger, mocked_stdout: StringIO) -> None:
    jlogger.info("main", "test", dataclass=ExamplePydanticDataclass(n=42, s="hello world"))
    assert mocked_stdout.getvalue().strip() == r'{"workflow":"main","message":"test","level":"INFO","dataclass":{"n":42,"s":"hello world"}}'

def test_json_logging_with_dict(jlogger: JsonLogger, mocked_stdout: StringIO) -> None:
    jlogger.info("main", "test", dict=dict(n=42, s="hello world"))
    assert mocked_stdout.getvalue().strip() == r'{"workflow":"main","message":"test","level":"INFO","dict":{"n":42,"s":"hello world"}}'