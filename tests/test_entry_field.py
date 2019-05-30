import unittest

from flags import Platform
from models import ChannelModel
from models.field import TextField, PlatformField, IntegerField, ArrayField
from models.field.exceptions import FieldTypeMismatch, FieldValueInvalid

test_seq = 1
test_platform = Platform.LINE
test_platform_id = int(test_platform)
test_token = 'C1234567890'


class TestChannelEntry(unittest.TestCase):
    json = {'p': test_platform_id, 't': test_token, 'mgr': ArrayField.none_obj()}

    def test_serialize(self):
        ce = ChannelModel(platform=test_platform, token=test_token)

        self.assertDictEqual(TestChannelEntry.json, ce.serialize())

    def test_parse(self):
        ce = ChannelModel.parse(TestChannelEntry.json)

        self.assertEqual(test_platform, ce.platform._value)
        self.assertEqual(test_token, ce.token._value)

    def test_new_instance(self):
        ce = ChannelModel(platform=test_platform, token=test_token)

        self.assertEqual(test_platform, ce.platform._value)
        self.assertEqual(test_token, ce.token._value)


class TestFieldFilter(unittest.TestCase):
    def test_intfield(self):
        field = IntegerField("n")

        field.value = 5
        self.assertEqual(5, field.value)
        with self.assertRaises(FieldTypeMismatch):
            field.value = None
        with self.assertRaises(FieldTypeMismatch):
            field.value = "5"

    def test_textfield(self):
        field = TextField("n")

        field.value = "S"
        self.assertEqual("S", field.value)
        with self.assertRaises(FieldTypeMismatch):
            field.value = 5
        with self.assertRaises(FieldTypeMismatch):
            field.value = None

        field2 = TextField("email", regex=r"^\w+@\w+")
        field2.value = "s@gmail.com"
        self.assertEqual("s@gmail.com", field2.value)
        with self.assertRaises(FieldValueInvalid):
            field2.value = "Lorem"

    def test_platformfield(self):
        field = PlatformField("n")

        field.value = Platform.LINE
        self.assertEqual(Platform.LINE, field.value)
        with self.assertRaises(FieldTypeMismatch):
            field.value = "LINE"
        with self.assertRaises(FieldTypeMismatch):
            field.value = None
        with self.assertRaises(FieldValueInvalid):
            field.value = 99999


if __name__ == '__main__':
    unittest.main()
