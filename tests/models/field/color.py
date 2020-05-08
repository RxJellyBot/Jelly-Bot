from django.test import TestCase

from extutils.color import Color, ColorFactory
from models.field import ColorField
from models.field.exceptions import (
    FieldTypeMismatch, FieldNoneNotAllowed
)


class TestColorField(TestCase):
    def test_properties(self):
        f = ColorField("cl")
        self.assertEquals("cl", f.key)
        self.assertTrue(f.auto_cast)
        self.assertFalse(f.read_only)
        self.assertFalse(f.stores_uid)
        self.assertEquals(ColorFactory.DEFAULT, f.default_value)
        self.assertEquals(Color, f.desired_type)
        self.assertTupleEqual((Color, int, str), f.expected_types)
        self.assertEquals(Color(5723991), f.cast_to_desired_type(5723991))
        self.assertEquals(Color(5723991), f.cast_to_desired_type("#575757"))
        with self.assertRaises(FieldNoneNotAllowed):
            f.cast_to_desired_type(None)
        self.assertEquals(ColorFactory.DEFAULT, f.none_obj())
        self.assertTrue(f.is_empty(None))
        self.assertTrue(f.is_empty(ColorFactory.DEFAULT))
        self.assertFalse(f.is_empty(ColorFactory.WHITE))

        self.assertFalse(f.allow_none)
        self.assertFalse(f.is_type_matched(None))
        self.assertFalse(f.is_value_valid(None))
        self.assertTrue(f.is_type_matched(ColorFactory.DEFAULT))
        self.assertTrue(f.is_value_valid(ColorFactory.DEFAULT))
        self.assertTrue(f.is_type_matched(8000))
        self.assertTrue(f.is_value_valid(8000))
        self.assertTrue(f.is_type_matched(-8000))
        self.assertFalse(f.is_value_valid(-8000))
        self.assertTrue(f.is_type_matched("#575757"))
        self.assertTrue(f.is_value_valid("#575757"))
        self.assertFalse(f.is_type_matched(True))
        self.assertFalse(f.is_value_valid(True))

    def test_properties_allow_none(self):
        f = ColorField("cl", allow_none=True)
        self.assertTrue(f.allow_none)
        self.assertTrue(f.is_type_matched(None))
        self.assertTrue(f.is_value_valid(None))
        self.assertTrue(f.is_type_matched(ColorFactory.DEFAULT))
        self.assertTrue(f.is_value_valid(ColorFactory.DEFAULT))
        self.assertTrue(f.is_type_matched(8000))
        self.assertTrue(f.is_value_valid(8000))
        self.assertTrue(f.is_type_matched(-8000))
        self.assertFalse(f.is_value_valid(-8000))
        self.assertTrue(f.is_type_matched("#575757"))
        self.assertTrue(f.is_value_valid("#575757"))
        self.assertFalse(f.is_type_matched(True))
        self.assertFalse(f.is_value_valid(True))

    def test_field_instance(self):
        f = ColorField("cl")
        fi = f.new()

        fi.value = ColorFactory.DEFAULT
        self.assertEqual(ColorFactory.DEFAULT, fi.value)
        fi.value = 5723991
        self.assertEqual(Color(5723991), fi.value)
        fi.value = "#575757"
        self.assertEqual(ColorFactory.from_hex("#575757"), fi.value)
        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None
        with self.assertRaises(FieldTypeMismatch):
            fi.value = True
        with self.assertRaises(FieldTypeMismatch):
            fi.value = []

    def test_field_instance_allow_none(self):
        f = ColorField("cl", allow_none=True)
        fi = f.new()

        fi.value = None
        self.assertIsNone(fi.value)
        fi.value = ColorFactory.DEFAULT
        self.assertEqual(ColorFactory.DEFAULT, fi.value)
        fi.value = 5723991
        self.assertEqual(Color(5723991), fi.value)
        fi.value = "#575757"
        self.assertEqual(ColorFactory.from_hex("#575757"), fi.value)
        with self.assertRaises(FieldTypeMismatch):
            fi.value = True
        with self.assertRaises(FieldTypeMismatch):
            fi.value = []

    def test_field_instance_not_allow_none(self):
        f = ColorField("af", allow_none=False)
        fi = f.new()

        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None
