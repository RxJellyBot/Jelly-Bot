import unittest
from datetime import datetime
from typing import Type, Any, Tuple

from bson import ObjectId

from models.field import ModelField, BaseField, IntegerField, BooleanField
from models.field.exceptions import (
    FieldTypeMismatch, FieldException, FieldModelClassInvalid
)
from models import Model, OID_KEY
from tests.base import TestCase

from ._test_val import TestFieldValue
from ._test_prop import TestFieldProperty

__all__ = ["TestModelFieldValueDefault", "TestModelFieldProperty", "TestModelFieldExtra",
           "TestModelFieldValueNoAutocast", "TestModelFieldValueNotAllowNone"]


class ModelTest(Model):
    Field1 = IntegerField("f1")
    Field2 = BooleanField("f2")


class ModelTest2(Model):
    Field1 = IntegerField("f1")
    Field2 = BooleanField("f2")


DUMMY_OID_1 = ObjectId.from_datetime(datetime.utcnow())
DUMMY_MODEL_DICT = {OID_KEY: DUMMY_OID_1, "f1": 5, "f2": True}
DUMMY_MODEL_INSTANCE = ModelTest.cast_model(DUMMY_MODEL_DICT)


class TestModelFieldProperty(TestFieldProperty):
    def get_field_class(self) -> Type[BaseField]:
        return ModelField

    def get_initialize_required_args(self) -> Tuple[Any, ...]:
        return ModelTest,

    def valid_not_none_obj_value(self) -> Any:
        return ModelTest(Id=DUMMY_OID_1)

    def expected_none_object(self) -> Any:
        return None

    def get_valid_default_values(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (ModelTest(Id=DUMMY_OID_1), ModelTest(Id=DUMMY_OID_1)),
            (DUMMY_MODEL_DICT, DUMMY_MODEL_INSTANCE),
            (DUMMY_MODEL_INSTANCE, DUMMY_MODEL_INSTANCE)
        )

    def get_invalid_default_values(self) -> Tuple[Any, ...]:
        return 5, "A", True, ModelTest2(Id=DUMMY_OID_1)

    def get_expected_types(self) -> Tuple[Type[Any], ...]:
        return ModelTest, dict

    def get_desired_type(self) -> Type[Any]:
        return ModelTest

    def test_auto_cast(self):
        self.assertTrue(self.get_initialized_field(auto_cast=False).auto_cast)
        self.assertTrue(self.get_initialized_field(auto_cast=True).auto_cast)

    @unittest.skip("`auto_cast` of `ModelField` always set to `True`.")
    def test_properties_default_valid_no_autocast(self):
        pass

    @unittest.skip("`allow_none` of `ModelField` always set to `True`.")
    def test_not_allow_none_set_default(self):
        pass

    @unittest.skip("`allow_none` of `ModelField` always set to `True`.")
    def test_not_allow_none_val_control(self):
        pass


class TestModelFieldValueDefault(TestFieldValue):
    def get_field(self) -> BaseField:
        return ModelField("k", ModelTest)

    def get_value_type_match_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (5, False),
            ("A", False),
            (True, False),
            (ModelTest(Id=DUMMY_OID_1), True),
            (ModelTest2(Id=DUMMY_OID_1), False),
            (DUMMY_MODEL_DICT, True),
            (DUMMY_MODEL_INSTANCE, True)
        )

    def get_value_validity_test(self) -> Tuple[Tuple[Any, bool], ...]:
        return (
            (None, True),
            (5, False),
            ("A", False),
            (True, False),
            (ModelTest(Id=DUMMY_OID_1), True),
            (ModelTest2(Id=DUMMY_OID_1), False),
            (DUMMY_MODEL_DICT, True),
            (DUMMY_MODEL_INSTANCE, True)
        )

    def is_auto_cast(self) -> bool:
        return True

    def get_values_to_cast(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (ModelTest(Id=DUMMY_OID_1), ModelTest(Id=DUMMY_OID_1)),
            (DUMMY_MODEL_DICT, DUMMY_MODEL_INSTANCE),
            (DUMMY_MODEL_INSTANCE, DUMMY_MODEL_INSTANCE)
        )

    def get_valid_value_to_set(self) -> Tuple[Tuple[Any, Any], ...]:
        return (
            (None, None),
            (ModelTest(Id=DUMMY_OID_1), ModelTest(Id=DUMMY_OID_1)),
            (DUMMY_MODEL_DICT, DUMMY_MODEL_INSTANCE),
            (DUMMY_MODEL_INSTANCE, DUMMY_MODEL_INSTANCE)
        )

    def get_invalid_value_to_set(self) -> Tuple[Tuple[Any, Type[FieldException]], ...]:
        return (
            (5, FieldTypeMismatch),
            ("A", FieldTypeMismatch),
            (True, FieldTypeMismatch),
            (ModelTest2(Id=DUMMY_OID_1), FieldTypeMismatch),
        )


class TestModelFieldValueNoAutocast(TestModelFieldValueDefault):
    def get_field(self) -> BaseField:
        return ModelField("k", ModelTest, auto_cast=False)


class TestModelFieldValueNotAllowNone(TestModelFieldValueDefault):
    def get_field(self) -> BaseField:
        return ModelField("k", ModelTest, allow_none=False)


class TestModelFieldExtra(TestCase):
    def test_non_model_cls(self):
        mdl_cls_to_test = [int, float, object(), BooleanField]

        for mdl_cls in mdl_cls_to_test:
            with self.subTest(mdl_cls=mdl_cls):
                with self.assertRaises(FieldModelClassInvalid):
                    ModelField("k", mdl_cls)


# These abstract classes will be instantiated (causing error) if not deleted
del TestFieldValue
del TestFieldProperty
