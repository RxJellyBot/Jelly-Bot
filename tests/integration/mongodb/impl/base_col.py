import os

from pymongo.errors import DuplicateKeyError

from tests.base import TestDatabaseMixin
from models import Model
from models.exceptions import InvalidModelFieldError, RequiredKeyNotFilledError, FieldKeyNotExistError
from models.field import IntegerField, BooleanField, ArrayField, ModelDefaultValueExt
from models.field.exceptions import FieldCastingFailedError, FieldValueInvalidError, FieldTypeMismatchError
from mongodb.factory import get_single_db_name, is_test_db, BaseCollection
from mongodb.factory.results import WriteOutcome
from tests.base import TestCase

__all__ = ["TestDbControl", "TestBaseCollection"]


class TestDbControl(TestCase):
    ORG_MONGO_DB = None
    ORG_TEST = None

    @classmethod
    def setUpTestClass(cls):
        cls.ORG_MONGO_DB = os.environ.get("MONGO_DB")
        cls.ORG_TEST = os.environ.get("TEST")

    @classmethod
    def tearDownTestClass(cls):
        if cls.ORG_MONGO_DB:
            os.environ["MONGO_DB"] = cls.ORG_MONGO_DB
        if cls.ORG_TEST:
            os.environ["TEST"] = cls.ORG_TEST

    def setUpTestCase(self) -> None:
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

        self.assertTrue(get_single_db_name().startswith("Test-"), get_single_db_name())

    def test_single_db_name_comb(self):
        os.environ["MONGO_DB"] = "singledb"
        os.environ["TEST"] = "1"

        self.assertEqual(get_single_db_name(), "singledb")

    def test_is_test_db(self):
        self.assertFalse(is_test_db("Test"))
        self.assertFalse(is_test_db("T-9999999999999"))
        self.assertFalse(is_test_db("Test-9999999999999"))
        self.assertTrue(is_test_db("Test-1590120034298"))


class TestBaseCollectionModel(Model):
    IntF = IntegerField("i", positive_only=True)
    BoolF = BooleanField("b", default=ModelDefaultValueExt.Required)
    ArrayF = ArrayField("a2", int, default=ModelDefaultValueExt.Optional, auto_cast=True)


class TestCollection(BaseCollection):
    database_name = "db"
    collection_name = "col"
    model_class = TestBaseCollectionModel


col = TestCollection()


class TestBaseCollection(TestDatabaseMixin):
    class CollectionTestNoColName(BaseCollection):
        database_name = "db"
        model_class = TestBaseCollectionModel

    class CollectionTestNoModelClass(BaseCollection):
        database_name = "db"
        collection_name = "col"

    @staticmethod
    def obj_to_clear():
        return [col]

    def test_col_missing_props(self):
        with self.assertRaises(AttributeError):
            TestBaseCollection.CollectionTestNoColName()
        with self.assertRaises(AttributeError):
            TestBaseCollection.CollectionTestNoModelClass()

    def test_insert_one_data(self):
        mdl, outcome, exception = col.insert_one_data(IntF=5, BoolF=True)

        self.assertIsNone(exception)
        self.assertEqual(outcome, WriteOutcome.O_INSERTED)
        self.assertIsInstance(mdl, TestBaseCollectionModel)
        self.assertEqual(mdl.int_f, 5)
        self.assertEqual(mdl.bool_f, True)
        self.assertIsNotNone(mdl.get_oid())

    def test_insert_one_data_type_mismatch(self):
        mdl, outcome, exception = col.insert_one_data(IntF="X", BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldTypeMismatchError)
        self.assertEqual(outcome, WriteOutcome.X_TYPE_MISMATCH)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_invalid(self):
        mdl, outcome, exception = col.insert_one_data(IntF=-5, BoolF=True)

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldValueInvalidError)
        self.assertEqual(outcome, WriteOutcome.X_INVALID_FIELD_VALUE)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_casting_failed(self):
        mdl, outcome, exception = col.insert_one_data(IntF=5, BoolF=True, ArrayF=[object()])

        self.assertIsInstance(exception, InvalidModelFieldError)
        self.assertIsInstance(exception.inner_exception, FieldCastingFailedError)
        self.assertEqual(outcome, WriteOutcome.X_CASTING_FAILED)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_missing_required(self):
        mdl, outcome, exception = col.insert_one_data()

        self.assertIsInstance(exception, RequiredKeyNotFilledError)
        self.assertEqual(outcome, WriteOutcome.X_REQUIRED_NOT_FILLED)
        self.assertIsNone(mdl)

    def test_insert_one_data_field_not_exist(self):
        mdl, outcome, exception = col.insert_one_data(BoolF=True, Bool2F=True)

        self.assertIsInstance(exception, FieldKeyNotExistError)
        self.assertEqual(outcome, WriteOutcome.X_MODEL_KEY_NOT_EXIST)
        self.assertIsNone(mdl)

    def test_insert_one_data_duplicated_key(self):
        col.create_index([("i", 1)], unique=True)

        col.insert_one_model(TestBaseCollectionModel(i=5, b=True, from_db=True))

        mdl, outcome, exception = col.insert_one_data(IntF=5, BoolF=True)

        self.assertIsInstance(exception, DuplicateKeyError)
        self.assertEqual(outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNotNone(mdl.get_oid())
