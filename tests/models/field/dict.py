from typing import Type, Any, Tuple

from models.field import DictionaryField, BaseField
from models.field.exceptions import (
    FieldTypeMismatch, FieldNoneNotAllowed, FieldException
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestDictFieldProperty", "TestDictFieldValueAllowNone",
           "TestDictFieldValueDefault", "TestDictFieldValueNoAutocast"]


class TestDictFieldProperty(TestFieldProperty):
    def get_field_class(self) -> Type[BaseField]:
        return DictionaryField

    def valid_not_none_value(self) -> Any:
        return {"A": 7}

    def expected_none_object(self) -> Any:
        return {}

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ({"A": 9}, {"A": 9}),
            ({}, {}),
            ({None: None}, {None: None})
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return [8], True, 7, [("A", 9), ("B", 8)]

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return dict,

    def get_desired_type(self) -> Type[Any]:
        return dict


class TestDictFieldValueDefault(TestFieldValue):
    def get_field(self) -> BaseField:
        return DictionaryField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ({}, True),
            ({None: None}, True),
            ({"A": 7}, True),
            ([("A", 9), ("B", 8)], False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            ({}, True),
            ({None: None}, True),
            ({"A": 7}, True),
            ([("A", 9), ("B", 8)], False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ({}, {}),
            ({None: None}, {None: None}),
            ({"A": 7}, {"A": 7}),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ({}, {}),
            ({None: None}, {None: None}),
            ({"A": 7}, {"A": 7}),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (7, FieldTypeMismatch),
            ([("A", 9), ("B", 8)], FieldTypeMismatch)
        )


class TestDictFieldValueAllowNone(TestFieldValue):
    def get_field(self) -> BaseField:
        return DictionaryField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ({}, True),
            ({None: None}, True),
            (True, False),
            ({"A": 7}, True),
            ([("A", 9), ("B", 8)], False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ({}, True),
            ({None: None}, True),
            (True, False),
            ({"A": 7}, True),
            ([("A", 9), ("B", 8)], False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ({}, {}),
            ({None: None}, {None: None}),
            ({"A": 7}, {"A": 7}),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ({}, {}),
            ({None: None}, {None: None}),
            ({"A": 7}, {"A": 7}),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (7, FieldTypeMismatch),
            ([("A", 9), ("B", 8)], FieldTypeMismatch)
        )


class TestDictFieldValueNoAutocast(TestFieldValue):
    def get_field(self) -> BaseField:
        return DictionaryField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, True),
            ({None: None}, True),
            (True, False),
            ({"A": 7}, True),
            ([("A", 9), ("B", 8)], False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ({}, True),
            ({None: None}, True),
            (True, False),
            ({"A": 7}, True),
            ([("A", 9), ("B", 8)], False)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ({}, {}),
            ({None: None}, {None: None}),
            ({"A": 7}, {"A": 7}),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ({}, {}),
            ({None: None}, {None: None}),
            ({"A": 7}, {"A": 7}),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (None, FieldNoneNotAllowed),
            (7, FieldTypeMismatch),
            ([("A", 9), ("B", 8)], FieldTypeMismatch)
        )


# These abstract classes will be instantiated (causing error) if not deleted
del TestFieldValue
del TestFieldProperty
