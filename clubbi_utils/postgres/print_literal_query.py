from typing import Callable, cast
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Selectable

from clubbi_utils.logging import logger


def print_literal_query(q: Selectable) -> None:
    dialect = cast(Callable, postgresql.dialect)()
    logger.info(q.compile(dialect=dialect, compile_kwargs=dict(literal_binds=True)))
