from datetime import datetime
from typing import Type, Any, Tuple

from bson import ObjectId

from models.field import ModelArrayField, BaseField, IntegerField, BooleanField
from models.field.exceptions import (
    FieldTypeMismatchError, FieldError, FieldModelClassInvalidError,
    FieldNoneNotAllowedError, FieldValueTypeMismatchError, FieldReadOnlyError
)
from models import Model, OID_KEY
from tests.base import TestCase

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestModelArrayFieldAllowNone", "TestModelArrayFieldExtra", "TestModelArrayFieldProperty",
           "TestModelArrayFieldValueDefault", "TestModelArrayFieldValueNoAutocast"]


class ModelTest(Model):
    Field1 = IntegerField("f1")
    Field2 = BooleanField("f2")


MODEL1 = ModelTest(Field1=7, Field2=True)
MODEL2 = ModelTest(Field1=9, Field2=True)
MODEL3 = ModelTest(Field1=11, Field2=True)

MODEL4_DICT = {OID_KEY: ObjectId.from_datetime(datetime.now()), "f1": 13, "f2": True}
MODEL4_INST = ModelTest.cast_model(MODEL4_DICT)


class TestModelArrayFieldProperty(TestFieldProperty.TestClass):
    def get_field_class(self) -> Type[BaseField]:
        return ModelArrayField

    def get_initialize_required_args(self) -> Tuple[Any, ...]:
        return ModelTest,

    def valid_not_none_obj_value(self) -> Any:
        return [MODEL1]

    def expected_none_object(self) -> Any:
        return []

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([MODEL1, MODEL2, MODEL3], [MODEL1, MODEL2, MODEL3]),
            ([MODEL1, MODEL2], [MODEL1, MODEL2]),
            ([MODEL1, MODEL3], [MODEL1, MODEL3]),
            ([MODEL1], [MODEL1]),
            ([MODEL4_DICT], [MODEL4_INST]),
            ([], [])
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return 7, "A", True, [7, 9]

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return list, tuple, set

    def get_desired_type(self) -> Type[Any]:
        return list


class TestModelArrayFieldValueDefault(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ModelArrayField("k", ModelTest)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (7, False),
            ("A", False),
            (True, False),
            ([], True),
            ([7, 9], False),
            ([MODEL1], True),
            ([MODEL1, MODEL2], True),
            ([MODEL1, MODEL2, MODEL3], True),
            ((MODEL1, MODEL2, MODEL3), True),
            ([MODEL4_DICT], True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (7, False),
            ("A", False),
            (True, False),
            ([], True),
            ([7, 9], False),
            ([MODEL1], True),
            ([MODEL1, MODEL2], True),
            ([MODEL1, MODEL2, MODEL3], True),
            ((MODEL1, MODEL2, MODEL3), True),
            ([MODEL4_DICT], True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([], []),
            ([MODEL1], [MODEL1]),
            ([MODEL1, MODEL2], [MODEL1, MODEL2]),
            ([MODEL1, MODEL2, MODEL3], [MODEL1, MODEL2, MODEL3]),
            ((MODEL1, MODEL2, MODEL3), [MODEL1, MODEL2, MODEL3]),
            ([MODEL4_DICT], [MODEL4_INST])
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([], []),
            ([MODEL1], [MODEL1]),
            ([MODEL1, MODEL2], [MODEL1, MODEL2]),
            ([MODEL1, MODEL2, MODEL3], [MODEL1, MODEL2, MODEL3]),
            ((MODEL1, MODEL2, MODEL3), [MODEL1, MODEL2, MODEL3]),
            ([MODEL4_DICT], [MODEL4_INST])
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            (7, FieldTypeMismatchError),
            ("A", FieldTypeMismatchError),
            (True, FieldTypeMismatchError),
            ([7, 9], FieldValueTypeMismatchError),
        )


class TestModelArrayFieldValueNoAutocast(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ModelArrayField("k", ModelTest, auto_cast=False)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (7, False),
            ("A", False),
            (True, False),
            ([], True),
            ([7, 9], False),
            ([MODEL1], True),
            ([MODEL1, MODEL2], True),
            ([MODEL1, MODEL2, MODEL3], True),
            ((MODEL1, MODEL2, MODEL3), True),
            ([MODEL4_DICT], True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, False),
            (7, False),
            ("A", False),
            (True, False),
            ([], True),
            ([7, 9], False),
            ([MODEL1], True),
            ([MODEL1, MODEL2], True),
            ([MODEL1, MODEL2, MODEL3], True),
            ((MODEL1, MODEL2, MODEL3), True),
            ([MODEL4_DICT], True)
        )

    def is_auto_cast(self) -> bool:
        return False

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([], []),
            ([MODEL1], [MODEL1]),
            ([MODEL1, MODEL2], [MODEL1, MODEL2]),
            ([MODEL1, MODEL2, MODEL3], [MODEL1, MODEL2, MODEL3]),
            ((MODEL1, MODEL2, MODEL3), [MODEL1, MODEL2, MODEL3]),
            ([MODEL4_DICT], [MODEL4_INST])
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            ([], []),
            ([MODEL1], [MODEL1]),
            ([MODEL1, MODEL2], [MODEL1, MODEL2]),
            ([MODEL1, MODEL2, MODEL3], [MODEL1, MODEL2, MODEL3]),
            ((MODEL1, MODEL2, MODEL3), (MODEL1, MODEL2, MODEL3)),
            ([MODEL4_DICT], [MODEL4_DICT])
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (None, FieldNoneNotAllowedError),
            (7, FieldTypeMismatchError),
            ("A", FieldTypeMismatchError),
            (True, FieldTypeMismatchError),
            ([7, 9], FieldValueTypeMismatchError),
        )


class TestModelArrayFieldAllowNone(TestFieldValue.TestClass):
    def get_field(self) -> BaseField:
        return ModelArrayField("k", ModelTest, allow_none=True)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (7, False),
            ("A", False),
            (True, False),
            ([], True),
            ([7, 9], False),
            ([MODEL1], True),
            ([MODEL1, MODEL2], True),
            ([MODEL1, MODEL2, MODEL3], True),
            ((MODEL1, MODEL2, MODEL3), True),
            ([MODEL4_DICT], True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (7, False),
            ("A", False),
            (True, False),
            ([], True),
            ([7, 9], False),
            ([MODEL1], True),
            ([MODEL1, MODEL2], True),
            ([MODEL1, MODEL2, MODEL3], True),
            ((MODEL1, MODEL2, MODEL3), True),
            ([MODEL4_DICT], True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ([], []),
            ([MODEL1], [MODEL1]),
            ([MODEL1, MODEL2], [MODEL1, MODEL2]),
            ([MODEL1, MODEL2, MODEL3], [MODEL1, MODEL2, MODEL3]),
            ((MODEL1, MODEL2, MODEL3), [MODEL1, MODEL2, MODEL3]),
            ([MODEL4_DICT], [MODEL4_INST])
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            ([], []),
            ([MODEL1], [MODEL1]),
            ([MODEL1, MODEL2], [MODEL1, MODEL2]),
            ([MODEL1, MODEL2, MODEL3], [MODEL1, MODEL2, MODEL3]),
            ((MODEL1, MODEL2, MODEL3), [MODEL1, MODEL2, MODEL3]),
            ([MODEL4_DICT], [MODEL4_INST])
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldError]], ...]:
        return (
            (7, FieldTypeMismatchError),
            ("A", FieldTypeMismatchError),
            (True, FieldTypeMismatchError),
            ([7, 9], FieldValueTypeMismatchError),
        )


class TestModelArrayFieldExtra(TestCase):
    def test_invalid_model_class(self):
        with self.assertRaises(FieldModelClassInvalidError):
            ModelArrayField("k", object)

    def test_readonly(self):
        f = ModelArrayField("k", ModelTest, readonly=True)
        fi = f.new()

        with self.assertRaises(FieldReadOnlyError):
            fi.value = [MODEL4_INST]
