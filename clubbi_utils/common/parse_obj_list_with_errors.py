from typing import Optional, Type, TypeVar, Any

from pydantic import parse_obj_as, ValidationError

from clubbi_utils.common.clubbi_validation_error import ClubbiValidationError, ErrorUnit

T = TypeVar("T")


def parse_obj_list_with_errors(type_: Type[T], obj: Any) -> tuple[list[T], Optional[ClubbiValidationError]]:
    """Parses a list of `obj` given a type `T` and returns a tuple containing the parsed result and errors,
    if a parsing error occurs the current value will be skiped and it's error will be appended in the errors result.

    Example:
    ```python
    from pydantic import BaseModel
    from clubbi_utils.common.parse_obj_list_with_errors import parse_obj_list_with_errors
    from clubbi_utils.common.clubbi_validation_error import ClubbiValidationError


    class Foo(BaseModel):
        a: int


    data = [{"a": 1}, {"a": "not a number"}, {"a": 2}]
    parsed_values, error = parse_obj_list_with_errors(Foo, data)

    assert parsed_values == [Foo(a=1), Foo(a=2)]
    assert error ==  ClubbiValidationError(
        errors=[
            {
                "identifier": "linha 2",
                "msg": "value is not a valid integer",
                "loc": "a",
                "type": "type_error.integer",
            }
        ],
        model="Foo",
    )
    ```
    """

    parsed_values: list[T] = []
    errors: list[ErrorUnit] = []
    type_qualname = type_.__qualname__
    if not isinstance(obj, list):
        validation_error = ClubbiValidationError(
            errors=[
                ErrorUnit(
                    identifier="0",
                    msg="Obj is not a list",
                    loc="0",
                    type="ValidationError",
                )
            ],
            model=type_qualname,
        )
        return [], validation_error
    for row_number, datum in enumerate(obj):
        try:
            parsed_value = parse_obj_as(type_, datum)
            parsed_values.append(parsed_value)
        except ValidationError as e:
            errors.extend(
                [
                    ErrorUnit(
                        identifier=f"linha {row_number + 1}",
                        msg=error["msg"],
                        loc=".".join(str(loc) for loc in error["loc"][1:]),
                        type=error["type"],
                    )
                    for error in e.errors()
                ]
            )
    if errors:
        return parsed_values, ClubbiValidationError(errors=errors, model=type_qualname)
    return parsed_values, None
