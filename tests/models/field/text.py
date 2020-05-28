from typing import Type, Any, Tuple

from django.utils.functional import Promise

from models.field import TextField, BaseField
from models.field.exceptions import (
    FieldTypeMismatchError, FieldNoneNotAllowedError, FieldEmptyValueNotAllowedError,
    FieldError, FieldMaxLengthReachedError, FieldRegexNotMatchError, FieldInvalidDefaultValueError
)
from tests.base import TestCase

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestTextFieldExtra", "TestTextFieldProperty", "TestTextFieldValueAllowNone",
           "TestTextFieldValueDefault", "TestTextFieldValueDifferentMaxLength", "TestTextFieldValueMustHaveContent",
           "TestTextFieldValueNoAutocast", "TestTextFieldValueWithRegex"]


class TestTextFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return TextField

    def valid_not_none_obj_value(self) -> Any:
        return "A"

    def expected_none_object(self) -> Any:
        return ""

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("A", "A"),
            ("OXX", "OXX"),
            ("", ""),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), "x" * (TextField.DEFAULT_MAX_LENGTH - 1)),
            ("x" * TextField.DEFAULT_MAX_LENGTH, "x" * TextField.DEFAULT_MAX_LENGTH),
            (True, "True"),
            (7, "7")
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return "x" * (TextField.DEFAULT_MAX_LENGTH + 1), [7, 9], {7: 9}, {7, 9}, (7, 9)

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return str, int, bool, Promise

    def get_desired_type(self) -> Type[Any]:
        return str


class TestTextFieldValueDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return TextField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("", True),
            ("A", True),
            ("OXX", True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), True),
            ("x" * TextField.DEFAULT_MAX_LENGTH, True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), True),
            (True, True),
            (7, True),
            (object(), False),
            ([7, 9], False),
            ({7: 9}, False),
            ({7, 9}, False),
            ((7, 9), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("", True),
            ("A", True),
            ("OXX", True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), True),
            ("x" * TextField.DEFAULT_MAX_LENGTH, True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), False),
            (True, True),
            (7, True),
            (object(), False),
            ([7, 9], False),
            ({7: 9}, False),
            ({7, 9}, False),
            ((7, 9), False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("", ""),
            ("A", "A"),
            ("OXX", "OXX"),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), "x" * (TextField.DEFAULT_MAX_LENGTH - 1)),
            ("x" * TextField.DEFAULT_MAX_LENGTH, "x" * TextField.DEFAULT_MAX_LENGTH),
            (True, "True"),
            (7, "7")
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("", ""),
            ("A", "A"),
            ("OXX", "OXX"),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), "x" * (TextField.DEFAULT_MAX_LENGTH - 1)),
            ("x" * TextField.DEFAULT_MAX_LENGTH, "x" * TextField.DEFAULT_MAX_LENGTH),
            (True, "True"),
            (7, "7")
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            (object(), FieldTypeMismatchError),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), FieldMaxLengthReachedError),
            ([7, 9], FieldTypeMismatchError),
            ({7: 9}, FieldTypeMismatchError),
            ({7, 9}, FieldTypeMismatchError),
            ((7, 9), FieldTypeMismatchError)
        )


class TestTextFieldValueAllowNone(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return TextField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("", True),
            ("A", True),
            ("OXX", True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), True),
            ("x" * TextField.DEFAULT_MAX_LENGTH, True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), True),
            (True, True),
            (7, True),
            (object(), False),
            ([7, 9], False),
            ({7: 9}, False),
            ({7, 9}, False),
            ((7, 9), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("", True),
            ("A", True),
            ("OXX", True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), True),
            ("x" * TextField.DEFAULT_MAX_LENGTH, True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), False),
            (True, True),
            (7, True),
            (object(), False),
            ([7, 9], False),
            ({7: 9}, False),
            ({7, 9}, False),
            ((7, 9), False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ("", ""),
            ("A", "A"),
            ("OXX", "OXX"),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), "x" * (TextField.DEFAULT_MAX_LENGTH - 1)),
            ("x" * TextField.DEFAULT_MAX_LENGTH, "x" * TextField.DEFAULT_MAX_LENGTH),
            (True, "True"),
            (7, "7")
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ("", ""),
            ("A", "A"),
            ("OXX", "OXX"),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), "x" * (TextField.DEFAULT_MAX_LENGTH - 1)),
            ("x" * TextField.DEFAULT_MAX_LENGTH, "x" * TextField.DEFAULT_MAX_LENGTH),
            (True, "True"),
            (7, "7")
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), FieldMaxLengthReachedError),
            (object(), FieldTypeMismatchError),
            ([7, 9], FieldTypeMismatchError),
            ({7: 9}, FieldTypeMismatchError),
            ({7, 9}, FieldTypeMismatchError),
            ((7, 9), FieldTypeMismatchError)
        )


class TestTextFieldValueNoAutocast(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return TextField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("", True),
            ("A", True),
            ("OXX", True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), True),
            ("x" * TextField.DEFAULT_MAX_LENGTH, True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), True),
            (True, True),
            (7, True),
            (object(), False),
            ([7, 9], False),
            ({7: 9}, False),
            ({7, 9}, False),
            ((7, 9), False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("", True),
            ("A", True),
            ("OXX", True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), True),
            ("x" * TextField.DEFAULT_MAX_LENGTH, True),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), False),
            (True, True),
            (7, True),
            (object(), False),
            ([7, 9], False),
            ({7: 9}, False),
            ({7, 9}, False),
            ((7, 9), False)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("", ""),
            ("A", "A"),
            ("OXX", "OXX"),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), "x" * (TextField.DEFAULT_MAX_LENGTH - 1)),
            ("x" * TextField.DEFAULT_MAX_LENGTH, "x" * TextField.DEFAULT_MAX_LENGTH),
            (True, "True"),
            (7, "7")
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("", ""),
            ("A", "A"),
            ("OXX", "OXX"),
            ("x" * (TextField.DEFAULT_MAX_LENGTH - 1), "x" * (TextField.DEFAULT_MAX_LENGTH - 1)),
            ("x" * TextField.DEFAULT_MAX_LENGTH, "x" * TextField.DEFAULT_MAX_LENGTH),
            (True, True),
            (7, 7)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            ("x" * (TextField.DEFAULT_MAX_LENGTH + 1), FieldMaxLengthReachedError),
            ([7, 9], FieldTypeMismatchError),
            ({7: 9}, FieldTypeMismatchError),
            ({7, 9}, FieldTypeMismatchError),
            ((7, 9), FieldTypeMismatchError),
            (object(), FieldTypeMismatchError)
        )


class TestTextFieldValueMustHaveContent(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return TextField("k", must_have_content=True, default="default")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            ("", True),
            ("X", True),
            ("XY", True),
            ("$&*)(@", True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            ("", False),
            ("X", True),
            ("XY", True),
            ("$&*)(@", True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("X", "X"),
            ("XY", "XY"),
            ("$&*)(@", "$&*)(@")
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("X", "X"),
            ("XY", "XY"),
            ("$&*)(@", "$&*)(@")
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("", FieldEmptyValueNotAllowedError),
        )


class TestTextFieldValueWithRegex(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return TextField("k", regex="[A-F]{8}", default="AAAAAAAA")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", True),
            ("AB", True),
            ("accc", True),
            ("abcdefab", True),
            ("ABCDEFAG", True),
            ("ABCDEFAB", True),
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", False),
            ("AB", False),
            ("accc", False),
            ("abcdefab", False),
            ("ABCDEFAG", False),
            ("ABCDEFAB", True),
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("ABCDEFAB", "ABCDEFAB"),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("ABCDEFAB", "ABCDEFAB"),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            ("A", FieldRegexNotMatchError),
            ("AB", FieldRegexNotMatchError),
            ("accc", FieldRegexNotMatchError),
            ("abcdefab", FieldRegexNotMatchError),
            ("ABCDEFAG", FieldRegexNotMatchError)
        )


class TestTextFieldValueDifferentMaxLength(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return TextField("k", maxlen=500)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", True),
            ("AAA", True),
            ("A" * 499, True),
            ("A" * 500, True),
            ("A" * 501, True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", True),
            ("AAA", True),
            ("A" * 499, True),
            ("A" * 500, True),
            ("A" * 501, False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("A", "A"),
            ("AAA", "AAA"),
            ("A" * 499, "A" * 499),
            ("A" * 500, "A" * 500)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("A", "A"),
            ("AAA", "AAA"),
            ("A" * 499, "A" * 499),
            ("A" * 500, "A" * 500)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("A" * 501, FieldMaxLengthReachedError),
        )


class TestTextFieldExtra(TestCase):
    def test_default_regex_not_match(self):
        with self.assertRaises(FieldInvalidDefaultValueError):
            TextField("k", default="ABCDE", regex=r"[A-E]{4}")

    def test_default_no_content(self):
        with self.assertRaises(FieldInvalidDefaultValueError):
            TextField("k", default="", must_have_content=True)
