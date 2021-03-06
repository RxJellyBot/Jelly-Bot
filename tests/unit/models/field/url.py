import unittest
from typing import Type, Any, Tuple

from models.field import UrlField, BaseField
from models.field.exceptions import (
    FieldTypeMismatchError, FieldNoneNotAllowedError, FieldError, FieldInvalidUrlError, FieldReadOnlyError
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestUrlFieldProperty", "TestUrlFieldValueAllowNone", "TestUrlFieldValueNotReadonly",
           "TestUrlFieldValueDefault", "TestUrlFieldValueNoAutocast"]


class TestUrlFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return UrlField

    def valid_not_none_obj_value(self) -> Any:
        return "https://google.com"

    def expected_none_object(self) -> Any:
        return ""

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("https://google.com", "https://google.com"),
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return True, 7, "A"

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return str,

    def get_desired_type(self) -> Type[Any]:
        return str

    def test_auto_cast(self):
        self.assertTrue(self.get_initialized_field(auto_cast=False).auto_cast)
        self.assertTrue(self.get_initialized_field(auto_cast=True).auto_cast)

    @unittest.skip("`auto_cast` of `UrlField` always set to `True`.")
    def test_properties_default_valid_no_autocast(self):
        pass


class TestUrlFieldValueDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return UrlField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            (7, False),
            ("X", True),
            ("https://google.com", True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            (7, False),
            ("X", False),
            ("https://google.com", True),
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("https://google.com", "https://google.com"),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return ()

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("https://google.com", FieldReadOnlyError),
            (None, FieldReadOnlyError),
            (True, FieldReadOnlyError),
            (7, FieldReadOnlyError),
            ("X", FieldReadOnlyError),
        )


class TestUrlFieldValueNoAutocast(TestUrlFieldValueDefault):
    def get_field(self) -> BaseField:
        return UrlField("k", auto_cast=False)


class TestUrlFieldValueAllowNone(TestUrlFieldValueDefault):
    def get_field(self) -> BaseField:
        return UrlField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, False),
            (7, False),
            ("X", True),
            ("https://google.com", True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (True, False),
            (7, False),
            ("X", False),
            ("https://google.com", True),
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ("https://google.com", "https://google.com"),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return ()

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldReadOnlyError),
            ("https://google.com", FieldReadOnlyError),
            (True, FieldReadOnlyError),
            (7, FieldReadOnlyError),
            ("X", FieldReadOnlyError),
        )


class TestUrlFieldValueNotReadonly(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return UrlField("k", readonly=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            (7, False),
            ("X", True),
            ("https://google.com", True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (True, False),
            (7, False),
            ("X", False),
            ("https://google.com", True),
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("https://google.com", "https://google.com"),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("https://google.com", "https://google.com"),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            (True, FieldTypeMismatchError),
            (7, FieldTypeMismatchError),
            ("X", FieldInvalidUrlError),
        )
