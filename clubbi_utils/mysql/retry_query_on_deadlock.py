import traceback
from typing import Any, Optional
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import Executable
from clubbi_utils.json_logging import jlogger

# https://dev.mysql.com/doc/mysql-errors/5.7/en/server-error-reference.html
_DEADLOCK_DETECTED_ERROR_CODE = 1213


def is_deadlock_error(operror: OperationalError) -> bool:
    return operror.orig.args[0] == _DEADLOCK_DETECTED_ERROR_CODE


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
            except OperationalError as operror:
                if not is_deadlock_error(operror):
                    raise
                jlogger.warning(
                    "retry_query_on_deadlock",
                    "deadlock_error",
                    str_err=str(operror),
                    repr_err=repr(operror),
                    traceback=traceback.format_exc(),
                    attempt=attempt + 1,
                )
                error = operror
    raise error
