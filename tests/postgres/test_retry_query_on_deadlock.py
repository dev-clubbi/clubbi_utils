from typing import Any, Optional
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call
from sqlalchemy.engine import Result
from sqlalchemy.exc import DBAPIError

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine
from sqlalchemy.sql import Executable

from clubbi_utils.postgres.retry_query_on_deadlock import retry_query_on_deadlock


class AsyncContextManagerMock:
    def __init__(self, aenter_return: AsyncMock) -> None:
        self._aenter_return = aenter_return

    async def __aenter__(self) -> AsyncMock:
        return self._aenter_return

    async def __aexit__(self, *args: Any) -> None:
        pass


class TestRetryQueryOnDeadlock(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self._conn = AsyncMock(spec=AsyncConnection)
        self._engine = AsyncMock(spec=AsyncEngine)
        self._engine.begin.side_effect = lambda: AsyncContextManagerMock(self._conn)
        self._statement = MagicMock(spec=Executable)
        self._dbapi_error_deadlock = DBAPIError("", "", orig=MagicMock(pgcode="40P01"))
        self._dbapi_error_other_error = DBAPIError("", "", orig=MagicMock(pgcode="21000"))
        self._result_mock = MagicMock(spec=Result)

    async def _run(
        self,
        maximum_number_of_retries: int,
        expected_number_of_execute_awaits: int,
        parameters: Optional[Any] = None,
    ) -> None:
        res = await retry_query_on_deadlock(self._engine, self._statement, parameters, maximum_number_of_retries)
        self.assertEqual(res, self._result_mock)
        self._conn.execute.assert_has_awaits(
            call(self._statement, parameters) for _ in range(expected_number_of_execute_awaits)
        )
        self._engine.begin.assert_has_calls(call() for _ in range(expected_number_of_execute_awaits))

    async def test_retry_on_deadlock_no_errors(self) -> None:
        self._conn.execute.return_value = self._result_mock
        await self._run(
            maximum_number_of_retries=8,
            expected_number_of_execute_awaits=1,
        )

    async def test_retry_on_deadlock_no_errors_with_parameters(self) -> None:
        self._conn.execute.return_value = self._result_mock
        await self._run(
            maximum_number_of_retries=8,
            expected_number_of_execute_awaits=1,
            parameters={"hello": "world"},
        )

    async def test_retry_on_deadlock_after_too_many_attempts(self) -> None:
        self._conn.execute.side_effect = self._dbapi_error_deadlock
        maximum_number_of_retries = 10
        with self.assertRaises(DBAPIError) as e:
            await self._run(
                maximum_number_of_retries=maximum_number_of_retries,
                expected_number_of_execute_awaits=0,
            )
        self.assertEqual(e.exception, self._dbapi_error_deadlock)
        self._conn.execute.assert_has_awaits(call(self._statement, None) for _ in range(maximum_number_of_retries))

    async def test_retry_on_deadlock_unknown_error(self) -> None:
        self._conn.execute.side_effect = self._dbapi_error_other_error
        with self.assertRaises(DBAPIError) as e:
            await self._run(
                maximum_number_of_retries=8,
                expected_number_of_execute_awaits=0,
            )
        self.assertEqual(e.exception, self._dbapi_error_other_error)

    async def test_retry_on_deadlock_unknown_error_after_tries(self) -> None:
        self._conn.execute.side_effect = [self._dbapi_error_deadlock for _ in range(5)] + [
            self._dbapi_error_other_error
        ]
        with self.assertRaises(DBAPIError) as e:
            await self._run(
                maximum_number_of_retries=8,
                expected_number_of_execute_awaits=0,
            )
        self.assertEqual(e.exception, self._dbapi_error_other_error)

    async def test_retry_on_deadlock_inside_number_of_errors_does_not_pass_the_limit(self) -> None:
        self._conn.execute.side_effect = [self._dbapi_error_deadlock for _ in range(5)] + [self._result_mock]
        await self._run(
            maximum_number_of_retries=8,
            expected_number_of_execute_awaits=6,
        )
