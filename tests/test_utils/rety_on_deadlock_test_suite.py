from typing import Any, Iterable, Optional, Protocol
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, call
from sqlalchemy.engine import Result

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine
from sqlalchemy.sql import Executable
from functools import partial


class AsyncContextManagerMock:
    def __init__(self, aenter_return: AsyncMock) -> None:
        self._aenter_return = aenter_return

    async def __aenter__(self) -> AsyncMock:
        return self._aenter_return

    async def __aexit__(self, *args: Any) -> None:
        """Async exit not needed, but need to be declared"""
        ...


class RetryQueryOnDeadlockCallable(Protocol):
    async def __call__(
        self,
        engine: AsyncEngine,
        statement: Executable,
        parameters: Optional[Any] = None,
        maximum_number_of_retries: int = 10,
    ) -> Result:
        ...


def attach_retry_on_deadlock_test_suite(
    test_case_type: type[IsolatedAsyncioTestCase],
    retry_query_on_deadlock: RetryQueryOnDeadlockCallable,
    expected_error_type: type[Exception],
    example_deadlock_error: Exception,
    example_non_deadlock_error: Exception,
) -> None:
    for test_method_name in RetryOnDeadlockTestsSuite._all_test_methods():
        test_suite = RetryOnDeadlockTestsSuite(
            retry_query_on_deadlock=retry_query_on_deadlock,
            expected_error_type=expected_error_type,
            example_deadlock_error=example_deadlock_error,
            example_non_deadlock_error=example_non_deadlock_error,
        )
        test_suite._attach_to_test_case(test_case_type, test_method_name)


class RetryOnDeadlockTestsSuite:
    def __init__(
        self,
        retry_query_on_deadlock: RetryQueryOnDeadlockCallable,
        expected_error_type: type[Exception],
        example_deadlock_error: Exception,
        example_non_deadlock_error: Exception,
    ) -> None:
        self._conn = AsyncMock(spec=AsyncConnection)
        self._engine = AsyncMock(spec=AsyncEngine)
        self._engine.begin.side_effect = lambda: AsyncContextManagerMock(self._conn)
        self._statement = MagicMock(spec=Executable)
        self._result_mock = MagicMock(spec=Result)
        self._example_deadlock_error = example_deadlock_error
        self._example_non_deadlock_error = example_non_deadlock_error
        self._retry_query_on_deadlock = retry_query_on_deadlock
        self._expected_error_type = expected_error_type

    @classmethod
    def _all_test_methods(cls) -> Iterable[str]:
        for attr in dir(cls):
            if not attr.startswith("test"):
                continue
            yield attr

    def _attach_to_test_case(self, test_case_type: type[IsolatedAsyncioTestCase], attr: str) -> None:
        test_method = getattr(self, attr)
        setattr(test_case_type, attr, lambda test_case: test_method(test_case))

    async def _run(
        self,
        test_case: IsolatedAsyncioTestCase,
        maximum_number_of_retries: int,
        expected_number_of_execute_awaits: int,
        parameters: Optional[Any] = None,
    ) -> None:
        res = await self._retry_query_on_deadlock(self._engine, self._statement, parameters, maximum_number_of_retries)
        test_case.assertEqual(res, self._result_mock)
        self._conn.execute.assert_has_awaits(
            call(self._statement, parameters) for _ in range(expected_number_of_execute_awaits)
        )
        self._engine.begin.assert_has_calls(call() for _ in range(expected_number_of_execute_awaits))

    async def test_retry_on_deadlock_no_errors(self, test_case: IsolatedAsyncioTestCase) -> None:
        self._conn.execute.return_value = self._result_mock
        await self._run(
            test_case=test_case,
            maximum_number_of_retries=8,
            expected_number_of_execute_awaits=1,
        )

    async def test_retry_on_deadlock_no_errors_with_parameters(self, test_case: IsolatedAsyncioTestCase) -> None:
        self._conn.execute.return_value = self._result_mock
        await self._run(
            test_case=test_case,
            maximum_number_of_retries=8,
            expected_number_of_execute_awaits=1,
            parameters={"hello": "world"},
        )

    async def test_retry_on_deadlock_after_too_many_attempts(self, test_case: IsolatedAsyncioTestCase) -> None:
        self._conn.execute.side_effect = self._example_deadlock_error
        maximum_number_of_retries = 10
        with test_case.assertRaises(self._expected_error_type) as e:
            await self._run(
                maximum_number_of_retries=maximum_number_of_retries,
                expected_number_of_execute_awaits=0,
                test_case=test_case,
            )
        test_case.assertEqual(e.exception, self._example_deadlock_error)
        self._conn.execute.assert_has_awaits(call(self._statement, None) for _ in range(maximum_number_of_retries))

    async def test_retry_on_deadlock_unknown_error(self, test_case: IsolatedAsyncioTestCase) -> None:
        self._conn.execute.side_effect = self._example_non_deadlock_error
        with test_case.assertRaises(self._expected_error_type) as e:
            await self._run(
                maximum_number_of_retries=8,
                expected_number_of_execute_awaits=0,
                test_case=test_case,
            )
        test_case.assertEqual(e.exception, self._example_non_deadlock_error)

    async def test_retry_on_deadlock_unknown_error_after_tries(self, test_case: IsolatedAsyncioTestCase) -> None:
        self._conn.execute.side_effect = [self._example_deadlock_error for _ in range(5)] + [
            self._example_non_deadlock_error
        ]
        with test_case.assertRaises(self._expected_error_type) as e:
            await self._run(
                maximum_number_of_retries=8,
                expected_number_of_execute_awaits=0,
                test_case=test_case,
            )
        test_case.assertEqual(e.exception, self._example_non_deadlock_error)

    async def test_retry_on_deadlock_inside_number_of_errors_does_not_pass_the_limit(
        self, test_case: IsolatedAsyncioTestCase
    ) -> None:
        self._conn.execute.side_effect = [self._example_deadlock_error for _ in range(5)] + [self._result_mock]
        await self._run(
            maximum_number_of_retries=8,
            expected_number_of_execute_awaits=6,
            test_case=test_case,
        )
