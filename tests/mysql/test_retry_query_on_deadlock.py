from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from sqlalchemy.exc import OperationalError
from clubbi_utils.mysql.retry_query_on_deadlock import retry_query_on_deadlock
from tests.test_utils.rety_on_deadlock_test_suite import RetryOnDeadlockTestsSuite


class TestMysqlRetryQueryOnDeadlock(IsolatedAsyncioTestCase):
    ...

test_suite = RetryOnDeadlockTestsSuite(
    retry_query_on_deadlock=retry_query_on_deadlock,
    example_deadlock_error=OperationalError("", "", orig=MagicMock(args=[1213])),
    example_non_deadlock_error=OperationalError("", "", orig=MagicMock(args=[1000])),
    expected_error_type=OperationalError,
)
test_suite.setup(TestMysqlRetryQueryOnDeadlock)
