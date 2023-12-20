from datetime import date
from typing import Optional
from unittest import TestCase

from pydantic import BaseModel, ValidationError

from clubbi_utils.common.pydantic_types import BrCompatibleDate, BrDate


class TestPydanticTypes(TestCase):
    def test_br_date(self) -> None:
        class Foo(BaseModel):
            date1: BrDate
            date2: Optional[BrDate]

        foo = Foo.parse_obj(
            {
                "date1": "20/12/2022",
                "date2": None,
            }
        )
        self.assertEqual(foo, Foo(date1=date(2022, 12, 20), date2=None))

        with self.assertRaises(ValidationError):
            Foo.parse_obj(
                {
                    "date1": "2022/12/20",
                    "date2": None,
                }
            )

    def test_br_compatible_date(self) -> None:
        class Foo(BaseModel):
            date1: Optional[BrCompatibleDate]
            date2: Optional[BrCompatibleDate]
            date3: Optional[BrCompatibleDate]

        foo = Foo.parse_obj(
            {
                "date1": "20/12/2022",
                "date2": "2022-12-20",
                "date3": None,
            }
        )

        self.assertEqual(foo, Foo(date1=date(2022, 12, 20), date2=date(2022, 12, 20), date3=None))

        with self.assertRaises(ValidationError):
            Foo.parse_obj(
                {
                    "date1": "2022/12/20",
                    "date2": "2022-12-20",
                    "date3": None,
                }
            )
