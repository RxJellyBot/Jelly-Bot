from datetime import datetime

from bson import InvalidDocument, ObjectId
from pymongo.errors import DuplicateKeyError

from extutils.mongo import get_codec_options
from mixin import ClearableMixin
from models import Model
from models.exceptions import InvalidModelFieldError, RequiredKeyNotFilledError, FieldKeyNotExistError
from models.field import IntegerField, BooleanField, ArrayField, ModelDefaultValueExt
from models.field.exceptions import FieldCastingFailedError, FieldValueInvalidError, FieldTypeMismatchError
from mongodb.factory import ControlExtensionMixin
from mongodb.factory.results import WriteOutcome, UpdateOutcome
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestControlExtensionMixin"]


class ModelTest(Model):
    IntF = IntegerField("i", positive_only=True)
    BoolF = BooleanField("b", default=ModelDefaultValueExt.Required)
    ArrayF = ArrayField("a", int, default=ModelDefaultValueExt.Optional, auto_cast=False)
    ArrayF2 = ArrayField("a2", int, default=ModelDefaultValueExt.Optional, auto_cast=True)


class ModelTest2(Model):
    def __init__(self, from_db=False):
        super().__init__(from_db=from_db)
        raise ValueError()


class CollectionTest(ControlExtensionMixin, ClearableMixin):
    model_class = ModelTest

    def clear(self):
        self.delete_many({})


class TestControlExtensionMixin(TestModelMixin, TestDatabaseMixin):
    collection = None

    @staticmethod
    def obj_to_clear():
        return [TestControlExtensionMixin.collection]

    @classmethod
    def setUpTestClass(cls):
        cls.collection = CollectionTest(
            database=cls.get_mongo_client().get_database(cls.get_db_name()),
            name="testcol",
            codec_options=get_codec_options())

    def test_insert_one_model(self):
        mdl = ModelTest(i=5, b=True, from_db=True)
        outcome, exception = self.collection.insert_one_model(mdl)

        self.assertIsNone(exception)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertIsNotNone(mdl.get_oid())

    def test_insert_one_model_not_serializable(self):
        outcome, exception = self.collection.insert_one_model(ModelTest(i=5, b=True, a={7}, from_db=True))

        self.assertIsInstance(exception, (AttributeError, InvalidDocument))
        self.assertEqual(outcome, WriteOutcome.X_NOT_SERIALIZABLE)

    def test_insert_one_model_duplicated_key(self):
        oid = ObjectId()
        mdl = ModelTest(i=5, b=True, from_db=True)
        mdl.set_oid(oid)

        self.collection.insert_one_model(mdl)

        outcome, exception = self.collection.insert_one_model(mdl)

        self.assertIsInstance(exception, DuplicateKeyError)
        self.assertEqual(outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertEqual(mdl.get_oid(), oid)

    def test_insert_one_data(self):
        mdl, outcome, exception = self.collection.insert_one_data(IntF=5, BoolF=True)

        self.assertIsNone(exception)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertIsInstance(mdl, ModelTest)
        self.assertEqual(mdl.int_f, 5)
        self.assertEqual(mdl.bool_f, True)
        self.assertIsNotNone(mdl.get_oid())

    def test_insert_one_data_type_mismatch(self):
        mdl, outcome, exception = self.collection.insert_one_data(IntF="X", BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldTypeMismatchError)
        self.assertEqual(outcome, WriteOutcome.X_TYPE_MISMATCH)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_invalid(self):
        mdl, outcome, exception = self.collection.insert_one_data(IntF=-5, BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldValueInvalidError)
        self.assertEqual(outcome, WriteOutcome.X_INVALID_FIELD_VALUE)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_casting_failed(self):
        mdl, outcome, exception = self.collection.insert_one_data(IntF=5, BoolF=True, ArrayF2=[object()])

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldCastingFailedError)
        self.assertEqual(outcome, WriteOutcome.X_CASTING_FAILED)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_missing_required(self):
        mdl, outcome, exception = self.collection.insert_one_data()

        self.assertIsInstance(exception, RequiredKeyNotFilledError)
        self.assertEqual(outcome, WriteOutcome.X_REQUIRED_NOT_FILLED)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_not_exist(self):
        mdl, outcome, exception = self.collection.insert_one_data(BoolF=True, Bool2F=True)

        self.assertIsInstance(exception, FieldKeyNotExistError)
        self.assertEqual(outcome, WriteOutcome.X_MODEL_KEY_NOT_EXIST)
        self.assertIsNone(mdl)

    def test_insert_one_data_duplicated_key(self):
        self.collection.create_index([("i", 1)], unique=True)

        self.collection.insert_one_model(ModelTest(i=5, b=True, from_db=True))

        mdl, outcome, exception = self.collection.insert_one_data(IntF=5, BoolF=True)

        self.assertIsInstance(exception, DuplicateKeyError)
        self.assertEqual(outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNotNone(mdl.get_oid())

        self.collection.drop_indexes()

    def test_insert_one_data_duplicated_compound_key(self):
        self.collection.create_index([("i", 1), ("b", 1)], unique=True)

        self.collection.insert_one_model(ModelTest(i=5, b=True, from_db=True))

        mdl, outcome, exception = self.collection.insert_one_data(IntF=5, BoolF=True)

        self.assertIsInstance(exception, DuplicateKeyError)
        self.assertEqual(outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNotNone(mdl.get_oid())

        self.collection.drop_indexes()

    def test_update_many_outcome(self):
        self.collection.insert_many([
            {"a": 7, "b": [8]},
            {"a": 7, "b": [10]}
        ])

        args_outcome = (
            (({"a": 7}, {"$unset": {"c": ""}}), UpdateOutcome.O_FOUND),
            (({"a": 7}, {"$unset": {"b": ""}}), UpdateOutcome.O_UPDATED),
            (({"d": 7}, {"$unset": {"b": ""}}), UpdateOutcome.X_NOT_FOUND)
        )

        for args, expected_outcome in args_outcome:
            with self.subTest(args=args, expected_outcome=expected_outcome):
                outcome = self.collection.update_many_outcome(*args)
                self.assertEqual(outcome, expected_outcome)

    def test_find_cursor_with_count(self):
        self.collection.insert_many([
            {"i": 7, "b": True},
            {"i": 8, "b": True}
        ])

        expected_mdls = (
            ModelTest(i=7, b=True, from_db=True),
            ModelTest(i=8, b=True, from_db=True)
        )

        crs = self.collection.find_cursor_with_count()

        self.assertEqual(2, len(crs))

        for actual_mdl, expected_mdl in zip(crs, expected_mdls):
            with self.subTest(expected_mdl):
                self.assertModelEqual(actual_mdl, expected_mdl)

    def test_find_cursor_with_count_with_date(self):
        self.collection.insert_many([
            {"_id": ObjectId.from_datetime(datetime(2020, 8, 21)), "i": 4, "b": True},
            {"_id": ObjectId.from_datetime(datetime(2020, 8, 22)), "i": 5, "b": True},
            {"_id": ObjectId.from_datetime(datetime(2020, 8, 23)), "i": 6, "b": True},
            {"_id": ObjectId.from_datetime(datetime(2020, 8, 24)), "i": 7, "b": True},
            {"_id": ObjectId.from_datetime(datetime(2020, 8, 25)), "i": 8, "b": True},
            {"_id": ObjectId.from_datetime(datetime(2020, 8, 26)), "i": 9, "b": True}
        ])

        expected_mdls = (
            ModelTest(i=6, b=True, from_db=True),
            ModelTest(i=7, b=True, from_db=True),
            ModelTest(i=8, b=True, from_db=True)
        )

        crs = self.collection.find_cursor_with_count(start=datetime(2020, 8, 22, 12), end=datetime(2020, 8, 25, 12))

        self.assertEqual(len(crs), 3)

        for actual_mdl, expected_mdl in zip(crs, expected_mdls):
            with self.subTest(expected_mdl):
                self.assertModelEqual(actual_mdl, expected_mdl)

    def test_find_one_casted(self):
        self.collection.insert_many([
            {"i": 7, "b": True},
            {"i": 8, "b": True}
        ])

        actual_mdl = self.collection.find_one_casted({"i": 7})

        self.assertModelEqual(actual_mdl, ModelTest(i=7, b=True, from_db=True))

    def test_attach_time_range(self):
        dt_start = datetime(2020, 5, 6)
        dt_end = datetime(2020, 5, 10)
        dt_start_oid = ObjectId.from_datetime(dt_start)
        dt_end_oid = ObjectId.from_datetime(dt_end)

        filter_actual = {}
        self.collection.attach_time_range(filter_actual, start=dt_start, end=dt_end)

        self.assertEqual(
            filter_actual,
            {
                "_id": {
                    "$gte": dt_start_oid,
                    "$lte": dt_end_oid
                }
            }
        )

    def test_attach_time_range_has_extra(self):
        dt_start = datetime(2020, 5, 6)
        dt_end = datetime(2020, 5, 10)
        dt_start_oid = ObjectId.from_datetime(dt_start)
        dt_end_oid = ObjectId.from_datetime(dt_end)

        filter_actual = {"a": 7}
        self.collection.attach_time_range(filter_actual, start=dt_start, end=dt_end)

        self.assertEqual(
            filter_actual,
            {
                "_id": {
                    "$gte": dt_start_oid,
                    "$lte": dt_end_oid
                },
                "a": 7
            }
        )

    def test_attach_time_range_has_extra_in_id(self):
        dt_start = datetime(2020, 5, 6)
        dt_end = datetime(2020, 5, 10)
        dt_start_oid = ObjectId.from_datetime(dt_start)
        dt_end_oid = ObjectId.from_datetime(dt_end)

        filter_actual = {"_id": {"a": "b"}}
        self.collection.attach_time_range(filter_actual, start=dt_start, end=dt_end)

        self.assertEqual(
            filter_actual,
            {
                "_id": {
                    "a": "b",
                    "$gte": dt_start_oid,
                    "$lte": dt_end_oid
                }
            }
        )

    def test_attach_time_range_has_lots_of_extra(self):
        dt_start = datetime(2020, 5, 6)
        dt_end = datetime(2020, 5, 10)
        dt_start_oid = ObjectId.from_datetime(dt_start)
        dt_end_oid = ObjectId.from_datetime(dt_end)

        filter_actual = {"_id": {"a": "b"}, "c": "d"}
        self.collection.attach_time_range(filter_actual, start=dt_start, end=dt_end)

        self.assertEqual(
            filter_actual,
            {
                "_id": {
                    "a": "b",
                    "$gte": dt_start_oid,
                    "$lte": dt_end_oid
                },
                "c": "d"
            }
        )
