from typing import Type, Any, Tuple

from models.field import FlagField, BaseField
from models.field.exceptions import (
    FieldTypeMismatchError, FieldNoneNotAllowedError, FieldFlagDefaultUndefinedError, FieldFlagNotFoundError,
    FieldError
)
from extutils.flags import FlagCodeEnum
from tests.base import TestCase

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestEnumNoDefault", "TestEnumWithDefaultProperty", "TestEnumWithDefaultValueAllowNone",
           "TestEnumWithDefaultValueDefault", "TestEnumWithDefaultValueNoAutocast"]


# region No default flags


class EnumNoDefault(FlagCodeEnum):
    A = 1
    B = 2


class EnumNoDefaultField(FlagField):
    FLAG_TYPE = EnumNoDefault


class TestEnumNoDefault(TestCase):
    def test_init(self):
        with self.assertRaises(FieldFlagDefaultUndefinedError):
            EnumNoDefaultField("a")


# endregion


# region Has default flags


class EnumWithDefault(FlagCodeEnum):
    @classmethod
    def default(cls):
        return EnumWithDefault.A

    A = 1
    B = 2


class EnumWithDefaultField(FlagField):
    FLAG_TYPE = EnumWithDefault


class TestEnumWithDefaultProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return EnumWithDefaultField

    def valid_not_none_obj_value(self) -> Any:
        return EnumWithDefault.B

    def expected_none_object(self) -> Any:
        return EnumWithDefault.A

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (EnumWithDefault.A, EnumWithDefault.A),
            (1, EnumWithDefault.A),
            ("A", EnumWithDefault.A),
            (2, EnumWithDefault.B),
            ("1", EnumWithDefault.A)
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return 3, True

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return EnumWithDefault, int, str

    def get_desired_type(self) -> Type[Any]:
        return EnumWithDefault


class TestEnumWithDefaultValueDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return EnumWithDefaultField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (EnumWithDefault.A, True),
            (EnumWithDefault.B, True),
            (2, True),
            (1, True),
            (3, True),
            ("1", True),
            ("A", True),
            ("C", True),
            (True, False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (EnumWithDefault.A, True),
            (EnumWithDefault.B, True),
            (2, True),
            (1, True),
            (3, False),
            ("1", True),
            ("A", True),
            ("C", False),
            (True, False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (EnumWithDefault.A, EnumWithDefault.A),
            (1, EnumWithDefault.A),
            (EnumWithDefault.B, EnumWithDefault.B),
            (2, EnumWithDefault.B),
            ("1", EnumWithDefault.A),
            ("A", EnumWithDefault.A)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (EnumWithDefault.A, EnumWithDefault.A),
            (1, EnumWithDefault.A),
            (EnumWithDefault.B, EnumWithDefault.B),
            (2, EnumWithDefault.B),
            ("1", EnumWithDefault.A),
            ("A", EnumWithDefault.A)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            (True, FieldTypeMismatchError),
            ("C", FieldFlagNotFoundError),
            (3, FieldFlagNotFoundError),
        )


class TestEnumWithDefaultValueNoAutocast(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return EnumWithDefaultField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (EnumWithDefault.A, True),
            (EnumWithDefault.B, True),
            (2, True),
            (1, True),
            (3, True),
            ("1", True),
            ("A", True),
            ("C", True),
            (True, False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (EnumWithDefault.A, True),
            (EnumWithDefault.B, True),
            (2, True),
            (1, True),
            (3, False),
            ("1", True),
            ("A", True),
            ("C", False),
            (True, False)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (EnumWithDefault.A, EnumWithDefault.A),
            (1, EnumWithDefault.A),
            (EnumWithDefault.B, EnumWithDefault.B),
            (2, EnumWithDefault.B),
            ("1", EnumWithDefault.A),
            ("A", EnumWithDefault.A)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (EnumWithDefault.A, EnumWithDefault.A),
            (1, 1),
            (EnumWithDefault.B, EnumWithDefault.B),
            (2, EnumWithDefault.B),
            ("1", "1"),
            ("A", "A")
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            (True, FieldTypeMismatchError),
            ("C", FieldFlagNotFoundError),
            (3, FieldFlagNotFoundError),
        )


class TestEnumWithDefaultValueAllowNone(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return EnumWithDefaultField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (EnumWithDefault.A, True),
            (EnumWithDefault.B, True),
            (2, True),
            (1, True),
            (3, True),
            ("1", True),
            ("A", True),
            ("C", True),
            (True, False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (EnumWithDefault.A, True),
            (EnumWithDefault.B, True),
            (2, True),
            (1, True),
            (3, False),
            ("1", True),
            ("A", True),
            ("C", False),
            (True, False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (EnumWithDefault.A, EnumWithDefault.A),
            (1, EnumWithDefault.A),
            (EnumWithDefault.B, EnumWithDefault.B),
            (2, EnumWithDefault.B),
            ("1", EnumWithDefault.A),
            ("A", EnumWithDefault.A)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (EnumWithDefault.A, EnumWithDefault.A),
            (1, EnumWithDefault.A),
            (EnumWithDefault.B, EnumWithDefault.B),
            (2, EnumWithDefault.B),
            ("1", EnumWithDefault.A),
            ("A", EnumWithDefault.A)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (True, FieldTypeMismatchError),
            ("C", FieldFlagNotFoundError),
            (3, FieldFlagNotFoundError),
        )


# endregion
