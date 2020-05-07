from django.test import TestCase

from models.field import BooleanField
from models.field.exceptions import (
    FieldTypeMismatch, FieldInvalidDefaultValue, FieldNoneNotAllowed
)


class TestBoolField(TestCase):
    def test_properties(self):
        f = BooleanField("b")
        self.assertFalse(f.allow_none)
        self.assertFalse(f.read_only)
        self.assertTrue(f.auto_cast)
        self.assertEquals("b", f.key)
        self.assertTupleEqual((bool, int), f.expected_types)
        self.assertEquals(bool, f.desired_type)
        self.assertFalse(f.default_value)
        self.assertFalse(f.stores_uid)

    def test_functions(self):
        f = BooleanField("b")
        self.assertFalse(f.is_type_matched(None))
        self.assertFalse(f.is_type_matched("G"))
        self.assertTrue(f.is_type_matched(True))
        self.assertTrue(f.is_type_matched(7))
        self.assertTrue(f.is_empty(None))
        self.assertFalse(f.is_empty(True))
        self.assertFalse(f.is_empty(7))
        self.assertFalse(f.is_empty("G"))

    def test_checks(self):
        f = BooleanField("b")
        with self.assertRaises(FieldNoneNotAllowed):
            f.check_value_valid(None)
        f.check_value_valid(True)
        f.check_value_valid(7)
        with self.assertRaises(FieldTypeMismatch):
            f.check_value_valid("G")

    def test_cast(self):
        f = BooleanField("b")
        self.assertTrue(f.cast_to_desired_type("G"))
        self.assertFalse(f.cast_to_desired_type(0))
        self.assertFalse(f.cast_to_desired_type(None))
        self.assertTrue(f.cast_to_desired_type(True))
        self.assertTrue(f.cast_to_desired_type(7))

        f = BooleanField("b", allow_none=True, auto_cast=False)
        self.assertTrue(f.cast_to_desired_type(7))
        self.assertFalse(f.cast_to_desired_type(0))
        self.assertTrue(f.cast_to_desired_type("G"))
        self.assertTrue(f.cast_to_desired_type(True))
        self.assertFalse(f.cast_to_desired_type(None))

    def test_field_instance(self):
        f = BooleanField("b", default=True)
        fi = f.new()
        self.assertTrue(fi.value)

        fi = f.new(True)
        self.assertTrue(fi.value)

        fi.value = 7
        self.assertTrue(fi.value)

        fi.value = True
        self.assertTrue(fi.value)

        with self.assertRaises(FieldTypeMismatch):
            fi.value = "G"

        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None

        f = BooleanField("b", allow_none=True, auto_cast=False)
        fi = f.new()
        self.assertFalse(fi.value)

        fi.value = 7
        self.assertEquals(7, fi.value)

        fi.value = True
        self.assertTrue(fi.value)

        with self.assertRaises(FieldTypeMismatch):
            fi.value = "G"

        fi.value = None
        self.assertFalse(fi.value)

    def test_field_invalid_default(self):
        with self.assertRaises(FieldInvalidDefaultValue):
            BooleanField("b", default="G")
