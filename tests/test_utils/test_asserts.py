from unittest import TestCase
from dataclasses import dataclass
from pydantic import BaseModel

from clubbi_utils.test_utils.asserts import assert_basemodel_equal, assert_dataclasses_equal


@dataclass
class ExampleDataClass:
    a: int
    b: str


class ExampleBaseModel(BaseModel):
    a: int
    b: str


class TestAssertFunctions(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._dataclass1 = ExampleDataClass(a=1, b="a")
        self._dataclass2 = ExampleDataClass(a=1, b="b")
        self._basemodel1 = ExampleBaseModel(a=1, b="a")
        self._basemodel2 = ExampleBaseModel(a=1, b="b")

    def test_assert_dataclasses_equal(self):
        assert_dataclasses_equal(self._dataclass1, self._dataclass1)

        with self.assertRaises(AssertionError):
            assert_dataclasses_equal(self._dataclass1, self._dataclass2)

    def test_assert_basemodel_equal(self):
        assert_basemodel_equal(self._basemodel1, self._basemodel1)

        with self.assertRaises(AssertionError):
            assert_basemodel_equal(self._basemodel1, self._basemodel2)
