import traceback
from typing import Any, Optional
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import Executable
from clubbi_utils.json_logging import jlogger

# https://www.postgresql.org/docs/8.2/errcodes-appendix.html
_DEADLOCK_DETECTED_ERROR_CODE = "40P01"


def is_deadlock_error(dbapie: DBAPIError) -> bool:
    return dbapie.orig.pgcode == _DEADLOCK_DETECTED_ERROR_CODE


async def retry_query_on_deadlock(
    engine: AsyncEngine,
    statement: Executable,
    parameters: Optional[Any] = None,
    maximum_number_of_retries: int = 10,
) -> Result:
    error: Exception
    for attempt in range(maximum_number_of_retries):
        async with engine.begin() as conn:
            try:
                return await conn.execute(statement, parameters)
            except DBAPIError as dbapie:
                if not is_deadlock_error(dbapie):
                    raise
                jlogger.warning(
                    "retry_query_on_deadlock",
                    "deadlock_error",
                    str_err=str(dbapie),
                    repr_err=repr(dbapie),
                    traceback=traceback.format_exc(),
                    attempt=attempt + 1,
                )
                error = dbapie
    raise error
