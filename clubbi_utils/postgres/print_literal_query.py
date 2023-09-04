from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Selectable

from clubbi_utils.logging import logger

def print_literal_query(q: Selectable) -> None:
    logger.info(q.compile(dialect=postgresql.dialect(), compile_kwargs=dict(literal_binds=True)))
