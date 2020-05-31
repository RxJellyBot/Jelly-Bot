from models import Model
from models.field import BooleanField, ModelField, ModelDefaultValueExt
from models.exceptions import RequiredKeyNotFilledError
from tests.base import TestCase

__all__ = ["TestNestedModel"]


class InnerModel(Model):
    Field = BooleanField("f", default=ModelDefaultValueExt.Required)


class OuterModel(Model):
    Field = ModelField("m", InnerModel)


class TestNestedModel(TestCase):
    def test_construct_required_filled(self):
        OuterModel(Field=InnerModel(Field=True))

    def test_construct_required_not_filled(self):
        with self.assertRaises(RequiredKeyNotFilledError):
            OuterModel(Field=InnerModel())

    def test_construct_attempt_use_default(self):
        with self.assertRaises(RequiredKeyNotFilledError):
            OuterModel()

    def test_outer_get_default_value(self):
        self.assertEqual(OuterModel.Field.default_value, ModelDefaultValueExt.Required)

    def test_inner_get_default_value(self):
        self.assertEqual(InnerModel.Field.default_value, ModelDefaultValueExt.Required)
