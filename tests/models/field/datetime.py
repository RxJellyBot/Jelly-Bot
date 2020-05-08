from datetime import datetime, timezone

from django.test import TestCase

from models.field import DateTimeField
from models.field.exceptions import (
    FieldTypeMismatch, FieldReadOnly,
    FieldInvalidDefaultValue, FieldNoneNotAllowed
)


class TestDatetimeField(TestCase):
    def test_properties(self):
        f = DateTimeField("af")
        self.assertEquals("af", f.key)
        self.assertTrue(f.auto_cast)
        self.assertFalse(f.read_only)
        self.assertFalse(f.stores_uid)
        self.assertEquals(datetime.min.replace(tzinfo=timezone.utc), f.default_value)
        self.assertEquals(datetime, f.desired_type)
        self.assertTupleEqual((datetime, str), f.expected_types)
        self.assertEquals(
            datetime(2020, 7, 2, 15, 0, 0, 0, tzinfo=timezone.utc),
            f.cast_to_desired_type("2020-07-02 15:00+0"))
        with self.assertRaises(FieldNoneNotAllowed):
            f.cast_to_desired_type(None)
        self.assertEquals(datetime.min.replace(tzinfo=timezone.utc), f.none_obj())
        self.assertTrue(f.is_empty(None))
        self.assertTrue(f.is_empty(datetime.min.replace(tzinfo=timezone.utc)))
        self.assertFalse(f.is_empty(datetime(2020, 7, 2, 15, 0, 0, 0, tzinfo=timezone.utc)))

        self.assertFalse(f.allow_none)
        self.assertFalse(f.is_type_matched(None))
        self.assertFalse(f.is_value_valid(None))
        self.assertTrue(f.is_type_matched("XSX"))
        self.assertFalse(f.is_value_valid("XSX"))
        self.assertTrue(f.is_value_valid("2020-07-02 15:00+7"))

    def test_properties_readonly(self):
        f = DateTimeField("af", readonly=False)
        self.assertFalse(f.read_only)

        fi = f.new()
        fi.value = datetime(2020, 7, 2, 15, 0, 0, 0, tzinfo=timezone.utc)

        f = DateTimeField("af", readonly=True)
        self.assertTrue(f.read_only)

        fi = f.new()
        with self.assertRaises(FieldReadOnly):
            fi.value = datetime(2020, 7, 2, 15, 0, 0, 0, tzinfo=timezone.utc)

    def test_properties_default(self):
        test_data = (
            (datetime(2020, 5, 2, 15, 0, 0), datetime(2020, 5, 2, 15, 0, 0, tzinfo=timezone.utc)),
            ("2020-05-02 15:00+0", datetime(2020, 5, 2, 15, 0, 0, tzinfo=timezone.utc))
        )

        for default_val, default_expected in test_data:
            with self.subTest(default_val=default_val):
                f = DateTimeField("af", default=default_val)
                fi = f.new()

                self.assertEquals(default_expected, fi.value)

    def test_properties_allow_none(self):
        f = DateTimeField("af", allow_none=True)
        self.assertTrue(f.allow_none)
        self.assertTrue(f.is_type_matched(None))
        self.assertTrue(f.is_value_valid(None))
        self.assertTrue(f.is_type_matched(datetime(2020, 5, 2, 15, 0, 0)))
        self.assertTrue(f.is_value_valid(datetime(2020, 5, 2, 15, 0, 0)))
        self.assertTrue(f.is_type_matched("XSX"))
        self.assertFalse(f.is_value_valid("XSX"))
        self.assertTrue(f.is_value_valid("2020-07-02 15:00+7"))

    def test_field_instance(self):
        f = DateTimeField("af")
        fi = f.new()

        fi.value = datetime(2020, 5, 2, 15, 0, 0)
        self.assertEqual(datetime(2020, 5, 2, 15, 0, 0, tzinfo=timezone.utc), fi.value)
        fi.value = "2020-07-02 15:00+0"
        self.assertEqual(datetime(2020, 7, 2, 15, 0, 0, tzinfo=timezone.utc), fi.value)
        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None
        with self.assertRaises(FieldTypeMismatch):
            fi.value = 7
        with self.assertRaises(FieldTypeMismatch):
            fi.value = True

    def test_field_instance_readonly(self):
        f = DateTimeField("af", readonly=True)
        fi = f.new()

        with self.assertRaises(FieldReadOnly):
            fi.value = datetime(2020, 5, 2, 15, 0, 0)

    def test_field_instance_allow_none(self):
        f = DateTimeField("af", allow_none=True)
        fi = f.new()

        fi.value = None
        self.assertIsNone(fi.value)

    def test_field_instance_not_allow_none(self):
        f = DateTimeField("af", allow_none=False)
        fi = f.new()

        with self.assertRaises(FieldNoneNotAllowed):
            fi.value = None

    def test_field_invalid_default(self):
        with self.assertRaises(FieldInvalidDefaultValue):
            DateTimeField("b", default=True)
        with self.assertRaises(FieldInvalidDefaultValue):
            DateTimeField("b", default=7)
        with self.assertRaises(FieldInvalidDefaultValue):
            DateTimeField("b", default="XXX")
