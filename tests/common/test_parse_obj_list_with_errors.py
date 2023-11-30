from unittest import TestCase

from pydantic import BaseModel
from clubbi_utils.common.clubbi_validation_error import ClubbiValidationError

from clubbi_utils.common.parse_obj_list_with_errors import parse_obj_list_with_errors


class Foo(BaseModel):
    a: int


class TestParseObjListWithErrors(TestCase):
    def test_parse_no_errors(self) -> None:
        data = [{"a": 1}, {"a": 2}]
        parsed_values, error = parse_obj_list_with_errors(Foo, data)
        self.assertEqual(parsed_values, [Foo(a=1), Foo(a=2)])
        self.assertIsNone(error)

    def test_parse_with_errors(self) -> None:
        data = [{"a": 1}, {"a": "not a number"}, {"a": 2}]
        parsed_values, error = parse_obj_list_with_errors(Foo, data)
        self.assertEqual(parsed_values, [Foo(a=1), Foo(a=2)])
        self.assertEqual(
            error,
            ClubbiValidationError(
                errors=[
                    {
                        "identifier": "linha 2",
                        "msg": "value is not a valid integer",
                        "loc": "a",
                        "type": "type_error.integer",
                    }
                ],
                model="Foo",
            ),
        )

    def test_parse_obj_not_list(self) -> None:
        parsed_values, error = parse_obj_list_with_errors(Foo, {})
        self.assertEqual(parsed_values, [])
        self.assertEqual(
            error,
            ClubbiValidationError(
                errors=[{"identifier": "0", "msg": "Obj is not a list", "loc": "0", "type": "ValidationError"}],
                model="Foo",
            ),
        )
