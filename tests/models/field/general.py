import unittest
from typing import Type, Any, Tuple

from models.field import GeneralField, BaseField
from models.field.exceptions import (
    FieldTypeMismatch, FieldException
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestGeneralFieldProperty", "TestGeneralFieldValueAutocast",
           "TestGeneralFieldValueDefault", "TestGeneralFieldValueNotAllowNone"]


class TestGeneralFieldProperty(TestFieldProperty):
    def get_field_class(self) -> Type[BaseField]:
        return GeneralField

    def valid_not_none_obj_value(self) -> Any:
        return "ABC"

    def expected_none_object(self) -> Any:
        return None

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("ABC", "ABC"),
            (7, str(7)),
            (True, str(True)),
            (None, None),
            ([5, 7], str([5, 7])),
            ({"A": "B"}, str({"A": "B"}))
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return (5, 9), {"A"}, object()

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return str, bool, int, list, dict

    def get_desired_type(self) -> Type[Any]:
        return str

    @unittest.skip("`allow_none` of `GenericField` always set to `True`.")
    def test_not_allow_none_set_default(self):
        pass

    @unittest.skip("`allow_none` of `GenericField` always set to `True`.")
    def test_not_allow_none_val_control(self):
        pass


class TestGeneralFieldValueDefault(TestFieldValue):
    def get_field(self) -> BaseField:
        return GeneralField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("ABC", True),
            (7, True),
            (True, True),
            ([5, 7], True),
            ({"A": "B"}, True),
            ((5, 9), False),
            ({"A"}, False),
            (object(), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("ABC", True),
            (7, True),
            (True, True),
            ([5, 7], True),
            ({"A": "B"}, True),
            ((5, 9), False),
            ({"A"}, False),
            (object(), False)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ("ABC", "ABC"),
            (7, str(7)),
            (True, str(True)),
            ([5, 7], str([5, 7])),
            ({"A": "B"}, str({"A": "B"})),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ("ABC", "ABC"),
            (7, 7),
            (True, True),
            ([5, 7], [5, 7]),
            ({"A": "B"}, {"A": "B"}),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            ((5, 9), FieldTypeMismatch),
            ({"A"}, FieldTypeMismatch),
            (object(), FieldTypeMismatch),
        )


class TestGeneralFieldValueNotAllowNone(TestGeneralFieldValueDefault):
    def get_field(self) -> BaseField:
        return GeneralField("k", allow_none=False)


class TestGeneralFieldValueAutocast(TestFieldValue):
    def get_field(self) -> BaseField:
        return GeneralField("k", auto_cast=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("ABC", True),
            (7, True),
            (True, True),
            ([5, 7], True),
            ({"A": "B"}, True),
            ((5, 9), False),
            ({"A"}, False),
            (object(), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("ABC", True),
            (7, True),
            (True, True),
            ([5, 7], True),
            ({"A": "B"}, True),
            ((5, 9), False),
            ({"A"}, False),
            (object(), False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ("ABC", "ABC"),
            (7, str(7)),
            (True, str(True)),
            ([5, 7], str([5, 7])),
            ({"A": "B"}, str({"A": "B"})),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ("ABC", "ABC"),
            (7, str(7)),
            (True, str(True)),
            ([5, 7], str([5, 7])),
            ({"A": "B"}, str({"A": "B"})),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            ((5, 9), FieldTypeMismatch),
            ({"A"}, FieldTypeMismatch),
            (object(), FieldTypeMismatch),
        )


# These abstract classes will be instantiated (causing error) if not deleted
del TestFieldValue
del TestFieldProperty
