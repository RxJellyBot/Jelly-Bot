from typing import Type, Any, Tuple

from models.field import IntegerField, BaseField
from models.field.exceptions import (
    FieldTypeMismatch, FieldException, FieldNoneNotAllowed, FieldValueNegative
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestIntegerFieldProperty", "TestIntegerFieldValueAllowNone",
           "TestIntegerFieldValueDefault", "TestIntegerFieldValueNoAutocast", "TestIntegerFieldValuePositiveOnly"]


class TestIntegerFieldProperty(TestFieldProperty):
    def get_field_class(self) -> Type[BaseField]:
        return IntegerField

    def valid_not_none_value(self) -> Any:
        return 5

    def expected_none_object(self) -> Any:
        return 0

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (5, 5),
            (-5, -5),
            (6.7, 6),
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return True, "A"

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return int, float

    def get_desired_type(self) -> Type[Any]:
        return int


class TestIntegerFieldValueDefault(TestFieldValue):
    def get_field(self) -> BaseField:
        return IntegerField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, True),
            (6.7, True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, True),
            (6.7, True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (0, 0),
            (5, 5),
            (-5, -5),
            (6.7, 6)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (0, 0),
            (5, 5),
            (-5, -5),
            (6.7, 6)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (True, FieldTypeMismatch),
            ("A", FieldTypeMismatch),
            (None, FieldNoneNotAllowed)
        )


class TestIntegerFieldValueNoAutocast(TestFieldValue):
    def get_field(self) -> BaseField:
        return IntegerField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, True),
            (6.7, True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, True),
            (6.7, True)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (0, 0),
            (5, 5),
            (-5, -5),
            (6.7, 6)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (0, 0),
            (5, 5),
            (-5, -5),
            (6.7, 6.7)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (True, FieldTypeMismatch),
            ("A", FieldTypeMismatch)
        )


class TestIntegerFieldValueAllowNone(TestFieldValue):
    def get_field(self) -> BaseField:
        return IntegerField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, True),
            (6.7, True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, True),
            (6.7, True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (0, 0),
            (5, 5),
            (-5, -5),
            (6.7, 6)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (0, 0),
            (5, 5),
            (-5, -5),
            (6.7, 6)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (True, FieldTypeMismatch),
            ("A", FieldTypeMismatch)
        )


class TestIntegerFieldValuePositiveOnly(TestFieldValue):
    def get_field(self) -> BaseField:
        return IntegerField("k", positive_only=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, True),
            (6.7, True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ("A", False),
            (0, True),
            (5, True),
            (-5, False),
            (6.7, True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (0, 0),
            (5, 5),
            (6.7, 6)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (0, 0),
            (5, 5),
            (6.7, 6)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (True, FieldTypeMismatch),
            ("A", FieldTypeMismatch),
            (-5, FieldValueNegative)
        )


# These abstract classes will be instantiated (causing error) if not deleted
del TestFieldValue
del TestFieldProperty
