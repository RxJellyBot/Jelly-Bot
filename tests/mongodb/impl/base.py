import os
from datetime import datetime

from bson import InvalidDocument, ObjectId
from django.test import TestCase
from pymongo.errors import DuplicateKeyError

from extutils.mongo import get_codec_options
from tests.base import TestDatabaseMixin
from models import Model
from models.exceptions import InvalidModelFieldError, RequiredKeyNotFilledError, FieldKeyNotExistError
from models.field import IntegerField, BooleanField, ArrayField, ModelDefaultValueExt
from models.field.exceptions import FieldCastingFailedError, FieldValueInvalidError, FieldTypeMismatchError
from mongodb.factory import get_single_db_name, is_test_db, ControlExtensionMixin, BaseCollection
from mongodb.factory.results import WriteOutcome

__all__ = ["TestDbControl", "TestControlExtensionMixin", "TestBaseCollection"]


class TestDbControl(TestCase):
    ORG_MONGO_DB = None
    ORG_TEST = None

    @classmethod
    def setUpClass(cls):
        cls.ORG_MONGO_DB = os.environ.get("MONGO_DB")
        cls.ORG_TEST = os.environ.get("TEST")

    @classmethod
    def tearDownClass(cls):
        if cls.ORG_MONGO_DB:
            os.environ["MONGO_DB"] = cls.ORG_MONGO_DB
        if cls.ORG_TEST:
            os.environ["TEST"] = cls.ORG_TEST

    def tearDown(self) -> None:
        if "MONGO_DB" in os.environ:
            del os.environ["MONGO_DB"]
        if "TEST" in os.environ:
            del os.environ["TEST"]

    def test_single_db_name_specified(self):
        os.environ["MONGO_DB"] = "singledb"

        self.assertEqual(get_single_db_name(), "singledb")

    def test_single_db_name_not_set(self):
        self.assertIsNone(get_single_db_name())

    def test_single_db_name_test(self):
        os.environ["TEST"] = "1"

        self.assertTrue(get_single_db_name().startswith("Test-"))

    def test_single_db_name_comb(self):
        os.environ["MONGO_DB"] = "singledb"
        os.environ["TEST"] = "1"

        self.assertEqual(get_single_db_name(), "singledb")

    def test_is_test_db(self):
        self.assertFalse(is_test_db("Test"))
        self.assertFalse(is_test_db("T-9999999999999"))
        self.assertFalse(is_test_db("Test-9999999999999"))
        self.assertTrue(is_test_db("Test-1590120034298"))


class TestControlExtensionMixin(TestDatabaseMixin):
    collection = None

    class CollectionTest(ControlExtensionMixin):
        pass

    class ModelTest(Model):
        IntF = IntegerField("i", positive_only=True)
        BoolF = BooleanField("b", default=ModelDefaultValueExt.Required)
        ArrayF = ArrayField("a", int, default=ModelDefaultValueExt.Optional, auto_cast=False)
        ArrayF2 = ArrayField("a2", int, default=ModelDefaultValueExt.Optional, auto_cast=True)

    class ModelTest2(Model):
        def __init__(self, from_db=False):
            super().__init__(from_db=from_db)
            raise ValueError()

    @classmethod
    def setUpTestClass(cls):
        cls.collection = TestControlExtensionMixin.CollectionTest(
            database=cls.get_mongo_client().get_database(cls.get_db_name()),
            name="testcol",
            codec_options=get_codec_options())

    def test_insert_one_model(self):
        mdl = TestControlExtensionMixin.ModelTest(i=5, b=True, from_db=True)
        outcome, exception = self.collection.insert_one_model(mdl)

        self.assertIsNone(exception)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertIsNotNone(mdl.get_oid())

    def test_insert_one_model_not_serializable(self):
        outcome, exception = self.collection.insert_one_model(
            TestControlExtensionMixin.ModelTest(i=5, b=True, a={7}, from_db=True))

        self.assertIsInstance(exception, (AttributeError, InvalidDocument))
        self.assertEqual(outcome, WriteOutcome.X_NOT_SERIALIZABLE)

    def test_insert_one_model_duplicated_key(self):
        oid = ObjectId()
        mdl = TestControlExtensionMixin.ModelTest(i=5, b=True, from_db=True)
        mdl.set_oid(oid)

        self.collection.insert_one_model(mdl)

        outcome, exception = self.collection.insert_one_model(mdl)

        self.assertIsInstance(exception, DuplicateKeyError)
        self.assertEqual(outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertEqual(mdl.get_oid(), oid)

    def test_insert_one_data(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(TestControlExtensionMixin.ModelTest, IntF=5, BoolF=True)

        self.assertIsNone(exception)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertIsInstance(mdl, TestControlExtensionMixin.ModelTest)
        self.assertEqual(mdl.int_f, 5)
        self.assertEqual(mdl.bool_f, True)
        self.assertIsNotNone(mdl.get_oid())

    def test_insert_one_data_not_model_cls(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(int, IntF=5, BoolF=True)

        self.assertIsNone(exception)
        self.assertEqual(outcome, WriteOutcome.X_NOT_MODEL)
        self.assertIsNone(mdl)

    def test_insert_one_data_type_mismatch(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(TestControlExtensionMixin.ModelTest, IntF="X", BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldTypeMismatchError)
        self.assertEqual(outcome, WriteOutcome.X_TYPE_MISMATCH)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_invalid(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(TestControlExtensionMixin.ModelTest, IntF=-5, BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldValueInvalidError)
        self.assertEqual(outcome, WriteOutcome.X_INVALID_FIELD)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_casting_failed(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(TestControlExtensionMixin.ModelTest,
                                            IntF=5, BoolF=True, ArrayF2=[object()])

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldCastingFailedError)
        self.assertEqual(outcome, WriteOutcome.X_CASTING_FAILED)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_missing_required(self):
        mdl, outcome, exception = self.collection.insert_one_data(TestControlExtensionMixin.ModelTest)

        self.assertIsInstance(exception, RequiredKeyNotFilledError)
        self.assertEqual(outcome, WriteOutcome.X_REQUIRED_NOT_FILLED)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_not_exist(self):
        mdl, outcome, exception = self.collection.insert_one_data(
            TestControlExtensionMixin.ModelTest, BoolF=True, Bool2F=True)

        self.assertIsInstance(exception, FieldKeyNotExistError)
        self.assertEqual(outcome, WriteOutcome.X_FIELD_NOT_EXIST)
        self.assertIsNone(mdl)

    def test_insert_one_data_construct_error(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(TestControlExtensionMixin.ModelTest2)

        self.assertIsInstance(exception, ValueError)
        self.assertEqual(outcome, WriteOutcome.X_CONSTRUCT_UNKNOWN)
        self.assertIsNone(mdl)

    def test_insert_one_data_duplicated_key(self):
        self.collection.create_index([("i", 1)], unique=True)

        self.collection.insert_one_model(TestControlExtensionMixin.ModelTest(i=5, b=True, from_db=True))

        mdl, outcome, exception = \
            self.collection.insert_one_data(TestControlExtensionMixin.ModelTest, IntF=5, BoolF=True)

        self.assertIsInstance(exception, DuplicateKeyError)
        self.assertEqual(outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNotNone(mdl.get_oid())

    def test_update_many_outcome(self):
        self.collection.insert_many([
            {"a": 7, "b": [8]},
            {"a": 7, "b": [10]}
        ])

        args_outcome = (
            (({"a": 7}, {"$unset": {"c": ""}}), WriteOutcome.O_DATA_EXISTS),
            (({"a": 7}, {"$unset": {"b": ""}}), WriteOutcome.O_DATA_UPDATED),
            (({"d": 7}, {"$unset": {"b": ""}}), WriteOutcome.X_NOT_FOUND)
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
            TestControlExtensionMixin.ModelTest(i=7, b=True, from_db=True),
            TestControlExtensionMixin.ModelTest(i=8, b=True, from_db=True)
        )

        crs = self.collection.find_cursor_with_count({}, parse_cls=TestControlExtensionMixin.ModelTest)

        self.assertEqual(2, len(crs))

        for actual_mdl, expected_mdl in zip(crs, expected_mdls):
            with self.subTest(expected_mdl):
                actual_mdl.clear_oid()
                self.assertEqual(actual_mdl, expected_mdl)

    def test_find_cursor_with_count_no_cls(self):
        self.collection.insert_many([
            {"i": 7, "b": True},
            {"i": 8, "b": True}
        ])

        expected_mdls = (
            {"i": 7, "b": True},
            {"i": 8, "b": True}
        )

        crs = self.collection.find_cursor_with_count({})

        self.assertEqual(2, len(crs))
        for actual_mdl, expected_mdl in zip(crs, expected_mdls):
            with self.subTest(expected_mdl):
                del actual_mdl["_id"]
                self.assertEqual(actual_mdl, expected_mdl)

    def test_find_one_casted(self):
        self.collection.insert_many([
            {"i": 7, "b": True},
            {"i": 8, "b": True}
        ])

        actual_mdl = self.collection.find_one_casted({"i": 7}, parse_cls=TestControlExtensionMixin.ModelTest)
        actual_mdl.clear_oid()

        self.assertEqual(actual_mdl, TestControlExtensionMixin.ModelTest(i=7, b=True, from_db=True))

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


class TestBaseCollectionModel(Model):
    IntF = IntegerField("i", positive_only=True)
    BoolF = BooleanField("b", default=ModelDefaultValueExt.Required)
    ArrayF = ArrayField("a2", int, default=ModelDefaultValueExt.Optional, auto_cast=True)


class TestBaseCollection(TestDatabaseMixin):
    collection = None

    class CollectionTest(BaseCollection):
        database_name = "db"
        collection_name = "col"
        model_class = TestBaseCollectionModel

    class CollectionTestNoDbName(BaseCollection):
        collection_name = "col"
        model_class = TestBaseCollectionModel

    class CollectionTestNoColName(BaseCollection):
        database_name = "db"
        model_class = TestBaseCollectionModel

    class CollectionTestNoModelClass(BaseCollection):
        database_name = "db"
        collection_name = "col"

    @classmethod
    def setUpTestClass(cls):
        cls.collection = TestBaseCollection.CollectionTest()

    def test_insert_one_data(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(IntF=5, BoolF=True)

        self.assertIsNone(exception)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertIsInstance(mdl, TestBaseCollectionModel)
        self.assertEqual(mdl.int_f, 5)
        self.assertEqual(mdl.bool_f, True)
        self.assertIsNotNone(mdl.get_oid())

    def test_insert_one_data_type_mismatch(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(IntF="X", BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldTypeMismatchError)
        self.assertEqual(outcome, WriteOutcome.X_TYPE_MISMATCH)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_invalid(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(IntF=-5, BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldValueInvalidError)
        self.assertEqual(outcome, WriteOutcome.X_INVALID_FIELD)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_casting_failed(self):
        mdl, outcome, exception = \
            self.collection.insert_one_data(IntF=5, BoolF=True, ArrayF=[object()])

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
        self.assertEqual(outcome, WriteOutcome.X_FIELD_NOT_EXIST)
        self.assertIsNone(mdl)

    def test_insert_one_data_duplicated_key(self):
        self.collection.create_index([("i", 1)], unique=True)

        self.collection.insert_one_model(TestControlExtensionMixin.ModelTest(i=5, b=True, from_db=True))

        mdl, outcome, exception = \
            self.collection.insert_one_data(IntF=5, BoolF=True)

        self.assertIsInstance(exception, DuplicateKeyError)
        self.assertEqual(outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNotNone(mdl.get_oid())
