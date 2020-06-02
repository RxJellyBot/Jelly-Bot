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

    def test_hash(self):
        hash(OuterModel(Field=InnerModel(Field=True)))

    def test_eq(self):
        self.assertEqual(OuterModel(Field=InnerModel(Field=True)),
                         OuterModel(Field=InnerModel(Field=True)))

    def test_set_differentiate(self):
        mdl = OuterModel(Field=InnerModel(Field=True))
        mdl2 = OuterModel(Field=InnerModel(Field=True))

        self.assertEqual({mdl} - {mdl2}, set())
        self.assertEqual({mdl}.difference({mdl2}), set())

    def test_set_differentiate_multi(self):
        s1 = {OuterModel(Field=InnerModel(Field=True)), OuterModel(Field=InnerModel(Field=False))}

        s2 = {OuterModel(Field=InnerModel(Field=True))}

        expected_s = {OuterModel(Field=InnerModel(Field=False))}

        self.assertEqual(s1 - s2, expected_s)
        self.assertEqual(s1.difference(s2), expected_s)
