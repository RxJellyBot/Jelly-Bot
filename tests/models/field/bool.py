from typing import Type, Any, Tuple

from models.field import BooleanField, BaseField
from models.field.exceptions import (
    FieldException, FieldNoneNotAllowed, FieldTypeMismatch
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestBoolFieldProperty", "TestBoolFieldValueDefault",
           "TestBoolFieldValueNoAutoCast", "TestBoolFieldValueAllowNone"]


class TestBoolFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return BooleanField

    def valid_not_none_obj_value(self) -> Any:
        return True

    def expected_none_object(self) -> Any:
        return False

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (False, False),
            (1, True),
            (0, False)
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return object(),

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return bool, int

    def get_desired_type(self) -> Type[Any]:
        return bool

    def json_schema(self, allow_additional=True) -> dict:
        return {
            "bsonType": "bool"
        }


class TestBoolFieldValueDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return BooleanField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, True),
            (False, True),
            (7, True),
            (1, True),
            (0, True),
            ("X", False),
            (object(), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, True),
            (False, True),
            (7, True),
            (1, True),
            (0, True),
            ("X", False),
            (object(), False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (True, True),
            (False, False),
            (7, True),
            (1, True),
            (0, False)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (True, True),
            (False, False),
            (7, True),
            (1, True),
            (0, False)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (object, FieldTypeMismatch),
            (None, FieldNoneNotAllowed),
            ("X", FieldTypeMismatch)
        )


class TestBoolFieldValueAllowNone(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return BooleanField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, True),
            (False, True),
            (7, True),
            (1, True),
            (0, True),
            ("X", False),
            (object(), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, True),
            (False, True),
            (7, True),
            (1, True),
            (0, True),
            ("X", False),
            (object(), False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (True, True),
            (False, False),
            (7, True),
            (1, True),
            (0, False)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (True, True),
            (False, False),
            (7, True),
            (1, True),
            (0, False)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (object, FieldTypeMismatch),
            ("X", FieldTypeMismatch)
        )


class TestBoolFieldValueNoAutoCast(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return BooleanField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, True),
            (False, True),
            (7, True),
            (1, True),
            (0, True),
            ("X", False),
            (object(), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, True),
            (False, True),
            (7, True),
            (1, True),
            (0, True),
            ("X", False),
            (object(), False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (True, True),
            (False, False),
            (7, True),
            (1, True),
            (0, False)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (True, True),
            (False, False),
            (7, True),
            (1, True),
            (0, False)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (object, FieldTypeMismatch),
            ("X", FieldTypeMismatch)
        )
