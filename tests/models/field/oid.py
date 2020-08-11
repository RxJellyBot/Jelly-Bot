from datetime import datetime
from typing import Type, Any, Tuple

from bson import ObjectId

from models import OID_KEY
from models.field import ObjectIDField, BaseField
from models.field.exceptions import (
    FieldTypeMismatchError, FieldNoneNotAllowedError, FieldOidStringInvalidError, FieldOidDatetimeOutOfRangeError,
    FieldError, FieldReadOnlyError
)

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestOidFieldProperty", "TestOidFieldValueAllowNone", "TestOidFieldValueDefault",
           "TestOidFieldValueNoAutocast", "TestOidFieldValueNoKey", "TestOidFieldValueNotReadonly",
           "TestOidFieldValueAllowNoneNotReadOnly"]


class TestOidFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return ObjectIDField

    def valid_not_none_obj_value(self) -> Any:
        return ObjectId.from_datetime(datetime(2020, 5, 9))

    def expected_none_object(self) -> Any:
        return ObjectId("000000000000000000000000")

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000"))
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return "A", 7, True, datetime(1920, 1, 1), datetime(2107, 1, 1)

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return ObjectId, str, datetime

    def get_desired_type(self) -> Type[Any]:
        return ObjectId


class TestOidFieldValueDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ObjectIDField("k")

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", True),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), True),
            (datetime(2107, 1, 1), True),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", False),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), False),
            (datetime(2107, 1, 1), False),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000"))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return ()

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (ObjectId("000000000000000000000000"), FieldReadOnlyError),
            ("5eb5f2800000000000000000", FieldReadOnlyError),
            (datetime(2020, 5, 9), FieldReadOnlyError),
            (None, FieldReadOnlyError),
            ("A", FieldReadOnlyError),
            (7, FieldReadOnlyError),
            (True, FieldReadOnlyError),
            (datetime(1920, 1, 1), FieldReadOnlyError),
            (datetime(2107, 1, 1), FieldReadOnlyError)
        )


class TestOidFieldValueNotReadonly(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ObjectIDField("k", readonly=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", True),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), True),
            (datetime(2107, 1, 1), True),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", False),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), False),
            (datetime(2107, 1, 1), False),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000"))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000"))
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            ("A", FieldOidStringInvalidError),
            (7, FieldTypeMismatchError),
            (True, FieldTypeMismatchError),
            (datetime(1920, 1, 1), FieldOidDatetimeOutOfRangeError),
            (datetime(2107, 1, 1), FieldOidDatetimeOutOfRangeError)
        )


class TestOidFieldValueAllowNone(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ObjectIDField("k", allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("A", True),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), True),
            (datetime(2107, 1, 1), True),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("A", False),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), False),
            (datetime(2107, 1, 1), False),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000"))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return ()

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldReadOnlyError),
            (ObjectId("000000000000000000000000"), FieldReadOnlyError),
            ("5eb5f2800000000000000000", FieldReadOnlyError),
            (datetime(2020, 5, 9), FieldReadOnlyError),
            ("A", FieldReadOnlyError),
            (7, FieldReadOnlyError),
            (True, FieldReadOnlyError),
            (datetime(1920, 1, 1), FieldReadOnlyError),
            (datetime(2107, 1, 1), FieldReadOnlyError)
        )


class TestOidFieldValueAllowNoneNotReadOnly(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ObjectIDField("k", allow_none=True, readonly=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("A", True),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), True),
            (datetime(2107, 1, 1), True),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            ("A", False),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), False),
            (datetime(2107, 1, 1), False),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000"))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000")),
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            ("A", FieldOidStringInvalidError),
            (7, FieldTypeMismatchError),
            (True, FieldTypeMismatchError),
            (datetime(1920, 1, 1), FieldOidDatetimeOutOfRangeError),
            (datetime(2107, 1, 1), FieldOidDatetimeOutOfRangeError)
        )


class TestOidFieldValueNoAutocast(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ObjectIDField("k", auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", True),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), True),
            (datetime(2107, 1, 1), True),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            ("A", False),
            (7, False),
            (True, False),
            (datetime(1920, 1, 1), False),
            (datetime(2107, 1, 1), False),
            (ObjectId("000000000000000000000000"), True),
            ("5eb5f2800000000000000000", True),
            (datetime(2020, 5, 9), True)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ObjectId("000000000000000000000000"), ObjectId("000000000000000000000000")),
            ("5eb5f2800000000000000000", ObjectId("5eb5f2800000000000000000")),
            (datetime(2020, 5, 9), ObjectId("5eb5f2800000000000000000"))
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return ()

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (ObjectId("000000000000000000000000"), FieldReadOnlyError),
            ("5eb5f2800000000000000000", FieldReadOnlyError),
            (datetime(2020, 5, 9), FieldReadOnlyError),
            (None, FieldReadOnlyError),
            ("A", FieldReadOnlyError),
            (7, FieldReadOnlyError),
            (True, FieldReadOnlyError),
            (datetime(1920, 1, 1), FieldReadOnlyError),
            (datetime(2107, 1, 1), FieldReadOnlyError)
        )


class TestOidFieldValueNoKey(TestOidFieldValueDefault):
    def get_field(self) -> BaseField:
        return ObjectIDField()

    def test_key_name(self):
        self.assertEqual(OID_KEY, self.get_field().key)
