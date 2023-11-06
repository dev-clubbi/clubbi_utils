from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import ANY, MagicMock, patch
from clubbi_utils.json_logging import JsonLogger
from clubbi_utils.common import timeit


class TestTimeit(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._jlogger_mock = MagicMock(spec=JsonLogger)
        self._jlogger_patch = patch("clubbi_utils.common.timeit.jlogger", self._jlogger_mock)
        self._jlogger_patch.start()

    def tearDown(self) -> None:
        self._jlogger_patch.stop()
        super().tearDown()

    def _get_jlogger_info_call(self) -> dict[str, Any]:
        self._jlogger_mock.info.assert_called_once()
        _, kwargs = self._jlogger_mock.info.call_args_list[0]
        return kwargs

    async def test_async_function(self) -> None:
        @timeit.with_timeit
        async def asyncfunc() -> None:
            return

        await asyncfunc()
        self.assertEqual(
            self._get_jlogger_info_call(),
            {
                "duration": ANY,
                "meta": {
                    "module": "test_timeit",
                    "qualname": "TestTimeit.test_async_function.<locals>.asyncfunc",
                },
            },
        )

    def test_sync_function(self) -> None:
        @timeit.with_timeit
        def syncfunc() -> None:
            return

        syncfunc()
        self.assertEqual(
            self._get_jlogger_info_call(),
            {
                "duration": ANY,
                "meta": {
                    "module": "test_timeit",
                    "qualname": "TestTimeit.test_sync_function.<locals>.syncfunc",
                },
            },
        )
