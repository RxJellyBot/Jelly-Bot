import math

from django.test import TestCase

from models.field import ArrayField, BooleanField
from models.field.exceptions import (
    FieldTypeMismatch, FieldReadOnly, FieldInstanceClassInvalid, FieldValueTypeMismatch,
    FieldMaxLengthReached, FieldInvalidDefaultValue, FieldNoneNotAllowed
)


class TestArrayField(TestCase):
    def test_properties(self):
        f = ArrayField("af", int)
        self.assertEquals("af", f.key)
        self.assertTrue(f.auto_cast)
        self.assertFalse(f.read_only)
        self.assertFalse(f.stores_uid)
        self.assertEquals(math.inf, f.max_len)
        self.assertListEqual([], f.default_value)
        self.assertEquals(list, f.desired_type)
        self.assertEquals((list, tuple, set), f.expected_types)
        self.assertEquals([7, 9], f.cast_to_desired_type(["7", "9"]))
        with self.assertRaises(FieldNoneNotAllowed):
            f.cast_to_desired_type(None)
        self.assertEquals([], f.none_obj())
        self.assertTrue(f.is_empty(None))
        self.assertTrue(f.is_empty([]))
        self.assertFalse(f.is_empty([7, 9]))

        self.assertFalse(f.allow_none)
        self.assertFalse(f.is_type_matched(None))
        self.assertFalse(f.is_value_valid(None))
        self.assertTrue(f.is_type_matched([]))
        self.assertTrue(f.is_value_valid([]))
        self.assertTrue(f.is_type_matched([7, 9]))
        self.assertTrue(f.is_value_valid([7, 9]))
        self.assertTrue(f.is_type_matched(["7", 9]))
        self.assertTrue(f.is_value_valid(["7", 9]))
        self.assertTrue(f.is_type_matched(["7", "9"]))
        self.assertTrue(f.is_value_valid(["7", "9"]))

    def test_properties_readonly(self):
        f = ArrayField("af", int, readonly=True)
        self.assertTrue(f.read_only)

    def test_properties_default(self):
        f = ArrayField("af", int, default=[7, 9])
        fi = f.new()
        self.assertListEqual([7, 9], fi.value)
        self.assertTrue(f.is_type_matched(["7", "9"]))

        f = ArrayField("af", int, default=["7", "9"])
        fi = f.new()
        self.assertListEqual([7, 9], fi.value)
        fi.value = []
        self.assertListEqual([], fi.value)
        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None

    def test_properties_allow_none(self):
        f = ArrayField("af", int, allow_none=True)
        self.assertTrue(f.allow_none)
        self.assertTrue(f.is_type_matched(None))
        self.assertTrue(f.is_value_valid(None))
        self.assertTrue(f.is_type_matched([]))
        self.assertTrue(f.is_value_valid([]))
        self.assertTrue(f.is_type_matched([7, 9]))
        self.assertTrue(f.is_value_valid([7, 9]))
        self.assertTrue(f.is_type_matched(["7", 9]))
        self.assertTrue(f.is_value_valid(["7", 9]))
        self.assertTrue(f.is_type_matched(["7", "9"]))
        self.assertTrue(f.is_value_valid(["7", "9"]))

        fi = f.new()
        fi.value = None
        self.assertIsNone(fi.value)
        fi.value = []
        self.assertEqual([], fi.value)
        fi.value = [7]
        self.assertEqual([7], fi.value)
        fi.value = [7, "9"]
        self.assertEqual([7, 9], fi.value)
        with self.assertRaises(FieldTypeMismatch):
            fi.value = "9"
        with self.assertRaises(FieldTypeMismatch):
            fi.value = 7

    def test_properties_auto_cast(self):
        f = ArrayField("af", int, auto_cast=False)
        fi = f.new()
        with self.assertRaises(FieldValueTypeMismatch):
            fi.value = ["7", "9"]
        with self.assertRaises(FieldValueTypeMismatch):
            fi.value = [7, "9"]
        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None
        with self.assertRaises(FieldTypeMismatch):
            fi.value = "9"
        with self.assertRaises(FieldTypeMismatch):
            fi.value = 7
        with self.assertRaises(FieldValueTypeMismatch):
            fi.value = [7, object()]

    def test_properties_allow_empty(self):
        f = ArrayField("af", int, allow_empty=False)
        self.assertFalse(f.is_value_valid([]))
        self.assertTrue(f.is_value_valid([7, 9, 10]))
        self.assertFalse(f.is_value_valid(None))

        f = ArrayField("af", int, allow_empty=False, allow_none=True)
        self.assertTrue(f.is_value_valid(None))

    def test_properties_inst_cls(self):
        with self.assertRaises(FieldInstanceClassInvalid):
            ArrayField("af", int, inst_cls=int)

    def test_properties_max_length(self):
        f = ArrayField("af", int, max_len=3)
        self.assertEquals(3, f.max_len)
        self.assertTrue(f.is_type_matched([1, 2]))
        self.assertTrue(f.is_value_valid([1, 2]))
        self.assertTrue(f.is_type_matched([1, 2, 3]))
        self.assertTrue(f.is_value_valid([1, 2, 3]))
        self.assertTrue(f.is_type_matched([1, 2, 3, 4]))
        self.assertFalse(f.is_value_valid([1, 2, 3, 4]))
        self.assertTrue(f.is_type_matched([1, 2, 3, 4, 7, 9]))
        self.assertFalse(f.is_value_valid([1, 2, 3, 4, 7, 9]))
        self.assertTrue(f.is_type_matched([1, 2, "3"]))
        self.assertTrue(f.is_value_valid([1, 2, "3"]))
        self.assertTrue(f.is_type_matched([1, "2"]))
        self.assertTrue(f.is_value_valid([1, "2"]))
        self.assertTrue(f.is_type_matched([]))
        self.assertTrue(f.is_value_valid([]))

        with self.assertRaises(FieldInvalidDefaultValue):
            ArrayField("af", int, max_len=5, default=[0, 1, 2, 3, 4, 5])
        with self.assertRaises(ValueError):
            ArrayField("af", int, max_len=-1)
        with self.assertRaises(TypeError):
            ArrayField("af", int, max_len=7.5)

    def test_element_type(self):
        f = ArrayField("af", bool)
        self.assertFalse(f.is_type_matched(None))
        self.assertFalse(f.is_value_valid(None))
        self.assertTrue(f.is_type_matched([]))
        self.assertTrue(f.is_value_valid([]))
        self.assertTrue(f.is_type_matched([7, 9]))
        self.assertTrue(f.is_value_valid([7, 9]))
        self.assertTrue(f.is_type_matched([True, 9]))
        self.assertTrue(f.is_value_valid([True, 9]))
        self.assertTrue(f.is_type_matched([True, True]))
        self.assertTrue(f.is_value_valid([True, True]))
        self.assertFalse(f.is_type_matched(9))
        self.assertFalse(f.is_value_valid(9))

    def test_field_instance(self):
        f = ArrayField("af", int)
        fi = f.new()

        fi.value = []
        self.assertListEqual([], fi.value)
        fi.value = [7]
        self.assertListEqual([7], fi.value)
        fi.value = [7, "9"]
        self.assertListEqual([7, 9], fi.value)
        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None
        with self.assertRaises(FieldTypeMismatch):
            fi.value = "9"
        with self.assertRaises(FieldTypeMismatch):
            fi.value = 7

    def test_field_instance_readonly(self):
        f = ArrayField("af", int, readonly=True)
        fi = f.new()

        with self.assertRaises(FieldReadOnly):
            fi.value = 7

    def test_field_instance_allow_none(self):
        f = ArrayField("af", int, allow_none=True)
        fi = f.new()

        fi.value = None
        self.assertIsNone(fi.value)

    def test_field_instance_not_allow_none(self):
        f = ArrayField("af", int, allow_none=False)
        fi = f.new()

        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None

    def test_field_instance_max_length(self):
        f = ArrayField("af", int, max_len=3)
        fi = f.new()

        fi.value = [7, 9, 11]
        self.assertListEqual([7, 9, 11], fi.value)
        fi.value = [8]
        self.assertListEqual([8], fi.value)
        with self.assertRaises(FieldMaxLengthReached):
            fi.value = [1, 2, 3, 4, 5, 6]


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
