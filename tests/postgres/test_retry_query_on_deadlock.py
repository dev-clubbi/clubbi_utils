from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from sqlalchemy.exc import DBAPIError
from clubbi_utils.postgres.retry_query_on_deadlock import retry_query_on_deadlock
from tests.test_utils.rety_on_deadlock_test_suite import RetryOnDeadlockTestsSuite


class TestPostgresRetryQueryOnDeadlock(IsolatedAsyncioTestCase):
    ...


test_suite = RetryOnDeadlockTestsSuite(
    retry_query_on_deadlock=retry_query_on_deadlock,
    example_deadlock_error=DBAPIError("", "", orig=MagicMock(pgcode="40P01")),
    example_non_deadlock_error=DBAPIError("", "", orig=MagicMock(pgcode="21000")),
    expected_error_type=DBAPIError,
)
test_suite.setup(TestPostgresRetryQueryOnDeadlock)
