from datetime import datetime as dt
from typing import Type, Any, Tuple

from django.utils import timezone as tz

from models.field import DateTimeField, BaseField
from models.field.exceptions import (
    FieldTypeMismatchError, FieldNoneNotAllowedError, FieldValueInvalidError, FieldError
)
from tests.base import TestCase

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestDatetimeFieldExtra", "TestDatetimeFieldProperty", "TestDatetimeFieldValueAllowNone",
           "TestDatetimeFieldValueDefault", "TestDatetimeFieldValueNoAutoCast"]


class TestDatetimeFieldExtra(TestCase):
    def test_value_is_utc(self):
        self.assertEqual(DateTimeField("dt").new().value.tzinfo, tz.utc)
        self.assertEqual(DateTimeField("dt", default=dt.now()).new().value.tzinfo, tz.utc)
        self.assertEqual(DateTimeField("dt", default=dt.utcnow()).new().value.tzinfo, tz.utc)


class TestDatetimeFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return DateTimeField

    def valid_not_none_obj_value(self) -> Any:
        return dt.now().replace(tzinfo=tz.utc)

    def expected_none_object(self) -> Any:
        return dt.min.replace(tzinfo=tz.utc)

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ("2020-05-07 8:00", dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc),
             dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return "XSX", True, 7

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return dt, str

    def get_desired_type(self) -> Type[Any]:
        return dt


class TestDatetimeFieldValueDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return DateTimeField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (dt.min.replace(tzinfo=tz.utc), True),
            ("2020-05-07 8:00", True),
            (dt(2020, 5, 7, 8), True),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc), True),
            ("XSX", True),
            (True, False),
            (7, False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (dt.min.replace(tzinfo=tz.utc), True),
            ("2020-05-07 8:00", True),
            (dt(2020, 5, 7, 8), True),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc), True),
            ("XSX", False),
            (True, False),
            (7, False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (dt.min.replace(tzinfo=tz.utc), dt.min.replace(tzinfo=tz.utc)),
            ("2020-05-07 8:00", dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8), dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc),
             dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (dt.min.replace(tzinfo=tz.utc), dt.min.replace(tzinfo=tz.utc)),
            ("2020-05-07 8:00", dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8), dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc),
             dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("XSX", FieldValueInvalidError),
            (True, FieldTypeMismatchError),
            (7, FieldTypeMismatchError),
            (None, FieldNoneNotAllowedError)
        )


class TestDatetimeFieldValueNoAutoCast(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return DateTimeField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (dt.min.replace(tzinfo=tz.utc), True),
            ("2020-05-07 8:00", True),
            (dt(2020, 5, 7, 8), True),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc), True),
            ("XSX", True),
            (True, False),
            (7, False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (dt.min.replace(tzinfo=tz.utc), True),
            ("2020-05-07 8:00", True),
            (dt(2020, 5, 7, 8), True),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc), True),
            ("XSX", False),
            (True, False),
            (7, False)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (dt.min.replace(tzinfo=tz.utc), dt.min.replace(tzinfo=tz.utc)),
            ("2020-05-07 8:00", dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8), dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc),
             dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (dt.min.replace(tzinfo=tz.utc), dt.min.replace(tzinfo=tz.utc)),
            ("2020-05-07 8:00", "2020-05-07 8:00"),
            (dt(2020, 5, 7, 8), dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc),
             dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("XSX", FieldValueInvalidError),
            (True, FieldTypeMismatchError),
            (7, FieldTypeMismatchError),
            (None, FieldNoneNotAllowedError)
        )


class TestDatetimeFieldValueAllowNone(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return DateTimeField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (dt.min.replace(tzinfo=tz.utc), True),
            ("2020-05-07 8:00", True),
            (dt(2020, 5, 7, 8), True),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc), True),
            ("XSX", True),
            (True, False),
            (7, False)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (dt.min.replace(tzinfo=tz.utc), True),
            ("2020-05-07 8:00", True),
            (dt(2020, 5, 7, 8), True),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc), True),
            ("XSX", False),
            (True, False),
            (7, False)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (dt.min.replace(tzinfo=tz.utc), dt.min.replace(tzinfo=tz.utc)),
            ("2020-05-07 8:00", dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8), dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc),
             dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (dt.min.replace(tzinfo=tz.utc), dt.min.replace(tzinfo=tz.utc)),
            ("2020-05-07 8:00", dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8), dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
            (dt(2020, 5, 7, 8).replace(tzinfo=tz.utc),
             dt(2020, 5, 7, 8).replace(tzinfo=tz.utc)),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("XSX", FieldValueInvalidError),
            (True, FieldTypeMismatchError),
            (7, FieldTypeMismatchError)
        )
