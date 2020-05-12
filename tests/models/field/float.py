from typing import Type, Any, Tuple

from models.field import FloatField, BaseField
from models.field.exceptions import (
    FieldTypeMismatch, FieldNoneNotAllowed, FieldException
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestFloatFieldDefault", "TestFloatFieldAllowNone", "TestFloatFieldNoAutocast", "TestFloatFieldProperty"]


class TestFloatFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return FloatField

    def valid_not_none_obj_value(self) -> Any:
        return 5.9

    def expected_none_object(self) -> Any:
        return 0.0

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (-7, -7.0),
            (-3.5, -3.5),
            (0, 0.0),
            (0.0, 0.0),
            (5, 5.0),
            (5.9, 5.9)
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return True, "A"

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return float, int

    def get_desired_type(self) -> Type[Any]:
        return float

    def json_schema(self, allow_additional=True) -> dict:
        return {
            "bsonType": "double"
        }


class TestFloatFieldDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return FloatField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (-7, True),
            (-3.5, True),
            (0, True),
            (0.0, True),
            (5, True),
            (5.9, True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (-7, True),
            (-3.5, True),
            (0, True),
            (0.0, True),
            (5, True),
            (5.9, True),
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (-7, -7.0),
            (-3.5, -3.5),
            (0, 0.0),
            (0.0, 0.0),
            (5, 5.0),
            (5.9, 5.9),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (-7, -7.0),
            (-3.5, -3.5),
            (0, 0.0),
            (0.0, 0.0),
            (5, 5.0),
            (5.9, 5.9),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (True, FieldTypeMismatch),
            ("A", FieldTypeMismatch),
        )


class TestFloatFieldAllowNone(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return FloatField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, False),
            ("A", False),
            (-7, True),
            (-3.5, True),
            (0, True),
            (0.0, True),
            (5, True),
            (5.9, True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, False),
            ("A", False),
            (-7, True),
            (-3.5, True),
            (0, True),
            (0.0, True),
            (5, True),
            (5.9, True),
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (-7, -7.0),
            (-3.5, -3.5),
            (0, 0.0),
            (0.0, 0.0),
            (5, 5.0),
            (5.9, 5.9),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (-7, -7.0),
            (-3.5, -3.5),
            (0, 0.0),
            (0.0, 0.0),
            (5, 5.0),
            (5.9, 5.9),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (True, FieldTypeMismatch),
            ("A", FieldTypeMismatch),
        )


class TestFloatFieldNoAutocast(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return FloatField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (-7, True),
            (-3.5, True),
            (0, True),
            (0.0, True),
            (5, True),
            (5.9, True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (-7, True),
            (-3.5, True),
            (0, True),
            (0.0, True),
            (5, True),
            (5.9, True),
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (-7, -7),
            (-3.5, -3.5),
            (0, 0),
            (0.0, 0.0),
            (5, 5),
            (5.9, 5.9),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (-7, -7),
            (-3.5, -3.5),
            (0, 0),
            (0.0, 0.0),
            (5, 5),
            (5.9, 5.9),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (True, FieldTypeMismatch),
            ("A", FieldTypeMismatch),
        )
