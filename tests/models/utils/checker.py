from datetime import datetime, timezone
from typing import Any, Dict

from bson import ObjectId
from django.conf import settings

from extutils.emailutils import EmailServer
from extutils.color import Color
from flags import AutoReplyContentType
from mongodb.factory import BaseCollection
from models import Model, ModelDefaultValueExt
from models.field import (
    ModelField, IntegerField, ModelArrayField, DictionaryField, FloatField, BooleanField, UrlField, TextField,
    ObjectIDField, GeneralField, DateTimeField, ColorField, ArrayField, AutoReplyContentTypeField
)
from models.utils import ModelFieldChecker
from tests.base import TestDatabaseMixin, TestCase

__all__ = ["TestDataChecker"]


class SubModel(Model):
    WITH_OID = False

    FInt = IntegerField("i2", default=8)


class ModelTest(Model):
    FModel = ModelField("m", SubModel)
    FInt = IntegerField("i", default=ModelDefaultValueExt.Required)
    FModelArray = ModelArrayField("ma", SubModel, default=ModelDefaultValueExt.Optional)
    FDict = DictionaryField("d")
    FFloat = FloatField("f", default=7.5)
    FBool = BooleanField("b")
    FUrl = UrlField("u", default=ModelDefaultValueExt.Optional)
    FText = TextField("t")
    FOid = ObjectIDField("o")
    FGeneral = GeneralField("g")
    FDatetime = DateTimeField("dt")
    FColor = ColorField("c")
    FArray = ArrayField("a", int, default=[17, 21])
    FArContent = AutoReplyContentTypeField("ac")


class CollectionTest(BaseCollection):
    database_name = "testchecker"
    collection_name = "testchecker"
    model_class = ModelTest


ColInst = CollectionTest()


class TestDataChecker(TestDatabaseMixin, TestCase):
    @staticmethod
    def collections_to_reset():
        return [ColInst]

    def setUpTestCase(self) -> None:
        self.default_dict = {
            "m": {"i2": 7},
            "i": 7,
            "ma": [{"i2": 9}, {"i2": 11}],
            "d": {"a": 10},
            "f": 8.5,
            "b": True,
            "u": "https://google.com",
            "t": "ABCDE",
            "o": ObjectId("5ebc47c97041fb2e814b59bb"),
            "g": 100,
            "dt": datetime(2020, 5, 7).replace(tzinfo=timezone.utc),
            "c": Color(5000000),
            "a": [5, 11, 13],
            "ac": AutoReplyContentType.TEXT
        }

    def data_field_repaired_test(self, key_to_repair: str, data: Dict[str, Any]):
        with self.subTest(data=data):
            if key_to_repair not in data:
                self.fail(f"`{key_to_repair}` not repaired.")

    def data_field_match_test(self, actual_data: Dict[str, Any], expected_values: Dict[str, Any]):
        # Cast to model to apply some type casting on fields (for example, making tz-aware datetime)
        # Cast back to dict/json for comparison effectiveness
        actual_data = ModelTest.cast_model(actual_data).to_json()

        for k, expected_v in expected_values.items():
            with self.subTest(key=k, expected_value=expected_v):
                self.assertTrue(k in actual_data)
                self.assertEqual(expected_v, actual_data[k])

    # region Main test body
    def missing_has_default(self, key_to_remove: str, expected_value_after_fill: Dict[str, Any]):
        # Setup data
        del self.default_dict[key_to_remove]
        ColInst.insert_one(self.default_dict)

        # Perform check
        ModelFieldChecker.check(ColInst)

        # Checking results
        self.assertEqual(ColInst.estimated_document_count(), 1, "Data unexpectedly lost.")

        data = ColInst.find_one()

        self.data_field_repaired_test(key_to_remove, data)

        expected_values = expected_value_after_fill
        expected_values.update(self.default_dict)

        self.data_field_match_test(data, expected_values)

    def missing_required(self, key_to_remove: str):
        # Setup data
        del self.default_dict[key_to_remove]
        ColInst.insert_one(self.default_dict)

        # Perform check
        ModelFieldChecker.check(ColInst)

        # Checking results
        self.assertEqual(ColInst.estimated_document_count(), 0, "Data not being moved out for repair.")
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0, "Mail not sent.")

    def missing_optional(self, key_to_remove: str):
        # Setup data
        del self.default_dict[key_to_remove]
        ColInst.insert_one(self.default_dict)

        # Perform check
        ModelFieldChecker.check(ColInst)

        # Checking results
        self.assertEqual(ColInst.estimated_document_count(), 1, "Data unexpectedly lost.")

        data = ColInst.find_one()

        self.data_field_match_test(data, self.default_dict)

    # endregion

    def test_repair_m(self):
        self.missing_has_default("m", {"m": SubModel.generate_default()})

    def test_repair_i(self):
        self.missing_required("i")

    def test_repair_ma(self):
        self.missing_optional("ma")

    def test_repair_d(self):
        self.missing_has_default("d", {"d": DictionaryField("k").none_obj()})

    def test_repair_f(self):
        self.missing_has_default("f", {"f": ModelTest.FFloat.default_value})

    def test_repair_b(self):
        self.missing_has_default("b", {"b": BooleanField("k").none_obj()})

    def test_repair_u(self):
        self.missing_optional("u")

    def test_repair_t(self):
        self.missing_has_default("t", {"t": TextField("k").none_obj()})

    def test_repair_o(self):
        self.missing_has_default("o", {"o": ObjectIDField("k").none_obj()})

    def test_repair_g(self):
        self.missing_has_default("g", {"g": GeneralField("k").none_obj()})

    def test_repair_dt(self):
        self.missing_has_default("dt", {"dt": DateTimeField("k").none_obj()})

    def test_repair_c(self):
        self.missing_has_default("c", {"c": ColorField("k").none_obj()})

    def test_repair_a(self):
        self.missing_has_default("a", {"a": ModelTest.FArray.default_value})

    def test_repair_ac(self):
        self.missing_has_default("ac", {"ac": AutoReplyContentType.default()})
