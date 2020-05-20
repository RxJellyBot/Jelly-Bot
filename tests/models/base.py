from bson import ObjectId
from django.test import TestCase

from flags import ModelValidityCheckResult
from models import Model, ModelDefaultValueExt
from models.field import IntegerField, BooleanField
from models.exceptions import (
    JsonKeyDuplicatedError, DeleteNotAllowed, FieldKeyNotExistedError, IdUnsupportedError, RequiredKeyUnfilledError
)

__all__ = ["TestBaseModel"]


class TestBaseModel(TestCase):
    # region Duplicated json key
    class DuplicateJsonModel(Model):
        Field1 = IntegerField("i")
        Field2 = BooleanField("i")

    def test_dup_json(self):
        with self.assertRaises(JsonKeyDuplicatedError):
            TestBaseModel.DuplicateJsonModel(Field1=7)

    # endregion

    # region Related to `__iter__()`
    class ModelIterNoPreIter(Model):
        Field1 = IntegerField("a")
        Field2 = IntegerField("b")

    class ModelIterPreIter(Model):
        Field1 = IntegerField("a")
        Field2 = IntegerField("b")

        def pre_iter(self):
            # noinspection PyAttributeOutsideInit
            self.field1 = 5

    def test_iter_has_pre(self):
        expected_vals = {
            "a": 5, "b": 0
        }
        mdl = TestBaseModel.ModelIterPreIter()

        for jk in mdl:
            self.assertEqual(mdl[jk], expected_vals[jk])

    def test_iter_no_pre(self):
        expected_vals = {
            "a": 0, "b": 0
        }
        mdl = TestBaseModel.ModelIterNoPreIter()

        for jk in mdl:
            self.assertEqual(mdl[jk], expected_vals[jk])

    def test_len(self):
        self.assertEqual(2, len(TestBaseModel.ModelIterPreIter()))
        self.assertEqual(2, len(TestBaseModel.ModelIterNoPreIter()))

    # endregion

    # region Invalid
    class TempInvalidException(Exception):
        pass

    class ModelOnInvalid(Model):
        Field1 = IntegerField("i")
        Field2 = BooleanField("b")

        def perform_validity_check(self) -> ModelValidityCheckResult:
            if self.field1 > 0:
                return ModelValidityCheckResult.X_UNCATEGORIZED
            else:
                return ModelValidityCheckResult.O_OK

        def on_invalid(self, reason=ModelValidityCheckResult.X_UNCATEGORIZED):
            raise TestBaseModel.TempInvalidException()

    def test_on_invalid(self):
        with self.assertRaises(TestBaseModel.TempInvalidException):
            _ = TestBaseModel.ModelOnInvalid(Field1=7)

        mdl = TestBaseModel.ModelOnInvalid()
        with self.assertRaises(TestBaseModel.TempInvalidException):
            mdl.field1 = 7

    # endregion

    # region OID
    class ModelHasOid(Model):
        Field1 = IntegerField("i")

    class ModelNoOid(Model):
        WITH_OID = False

        Field1 = IntegerField("i")

    def check_oid_not_exists(self, mdl):
        with self.assertRaises(FieldKeyNotExistedError if mdl.WITH_OID else IdUnsupportedError):
            _ = mdl.id
        self.assertIsNone(mdl.get_oid())
        with self.assertRaises(KeyError if mdl.WITH_OID else IdUnsupportedError):
            _ = mdl["_id"]
        self.assertIsNone(mdl.get("_id"))

    def check_oid_match(self, mdl, oid):
        self.assertEqual(mdl.id, oid)
        self.assertEqual(mdl.get_oid(), oid)
        self.assertEqual(mdl["_id"], oid)
        self.assertEqual(mdl.get("_id"), oid)

    def test_oid_ops_has_oid(self):
        mdl = TestBaseModel.ModelHasOid()
        oid = ObjectId()

        self.check_oid_not_exists(mdl)

        mdl.set_oid(oid)

        self.check_oid_match(mdl, oid)

        mdl.clear_oid()

        self.check_oid_not_exists(mdl)

    def test_oid_ops_no_oid(self):
        mdl = TestBaseModel.ModelNoOid()
        oid = ObjectId()

        self.check_oid_not_exists(mdl)

        with self.assertRaises(IdUnsupportedError):
            mdl.set_oid(oid)

        self.check_oid_not_exists(mdl)

        mdl.clear_oid()

        self.check_oid_not_exists(mdl)

    # endregion

    # region Miscellaneous
    class TestModel(Model):
        Field1 = IntegerField("f1")
        Field2 = IntegerField("f2", default=ModelDefaultValueExt.Required)
        Field3 = IntegerField("f3", default=ModelDefaultValueExt.Optional)
        Field4 = IntegerField("f4", default=5)

    def test_del(self):
        d = {"f1": 1, "f2": 2, "f3": 3, "f4": 4}

        for k in d.keys():
            mdl = TestBaseModel.TestModel.cast_model(d)
            with self.assertRaises(DeleteNotAllowed):
                del mdl[k]

    def test_to_json(self):
        d = {"f1": 1, "f2": 2, "f3": 3, "f4": 4}
        mdl = TestBaseModel.TestModel.cast_model(d)

        self.assertDictEqual(mdl.to_json(), d)

    def test_generate_default(self):
        # No value given (Required value also not given)
        with self.assertRaises(RequiredKeyUnfilledError):
            TestBaseModel.TestModel.generate_default()

        # Required value provided
        mdl = TestBaseModel.TestModel.generate_default(Field2=5)
        expected = {"f1": 0, "f2": 5, "f4": 5}
        self.assertEqual(mdl.to_json(), expected)

        # Optional value provided
        mdl = TestBaseModel.TestModel.generate_default(Field2=5, Field3=4)
        expected = {"f1": 0, "f2": 5, "f3": 4, "f4": 5}
        self.assertEqual(mdl.to_json(), expected)

        # Default value overridden
        mdl = TestBaseModel.TestModel.generate_default(Field2=5, Field4=7)
        expected = {"f1": 0, "f2": 5, "f4": 7}
        self.assertEqual(mdl.to_json(), expected)

    # region Operations on json key / field key
    def test_model_fields(self):
        fs = {
            TestBaseModel.TestModel.Field1,
            TestBaseModel.TestModel.Field2,
            TestBaseModel.TestModel.Field3,
            TestBaseModel.TestModel.Field4,
            Model.Id,
        }

        self.assertSetEqual(TestBaseModel.TestModel.model_fields(), fs)

    def test_model_field_keys(self):
        fs = {"Id", "Field1", "Field2", "Field3", "Field4"}

        self.assertSetEqual(TestBaseModel.TestModel.model_field_keys(), fs)

    def test_model_json_keys(self):
        fs = {"_id", "f1", "f2", "f3", "f4"}

        self.assertSetEqual(TestBaseModel.TestModel.model_json_keys(), fs)

    def test_json_key_to_field(self):
        trans = {"_id": "Id", "f1": "Field1", "f2": "Field2", "f3": "Field3", "f4": "Field4"}

        for jk in TestBaseModel.TestModel.model_json_keys():
            with self.subTest(jk=jk):
                if jk not in trans:
                    self.fail(f"Json key {jk} not in the `trans` dict.")

                fk = trans[jk]

                self.assertEqual(TestBaseModel.TestModel.json_key_to_field(jk), fk)

    def test_field_to_json_key(self):
        trans = {"Field1": "f1", "Field2": "f2", "Field3": "f3", "Field4": "f4", "Id": "_id"}

        for fk in TestBaseModel.TestModel.model_field_keys():
            with self.subTest(fk=fk):
                if fk not in trans:
                    self.fail(f"Field key {fk} not in the `trans` dict.")

                jk = trans[fk]

                self.assertEqual(TestBaseModel.TestModel.field_to_json_key(fk), jk)

    # endregion

    # region Operations on fields
    def test_is_field_none(self):
        is_none = {
            "Field1": True,
            "Field2": False,
            "Field3": True,
            "Field4": True,
            "Field5": True
        }
        not_exists = {"Field5"}
        mdl = TestBaseModel.TestModel.cast_model({"f1": 0, "f2": 5, "f3": 0, "f4": 0})

        for fk, result in is_none.items():
            with self.subTest(fk=fk, expected_result=result):
                self.assertEqual(mdl.is_field_none(fk, raise_on_not_exists=False), result)

        for fk in not_exists:
            with self.subTest(fk=fk):
                with self.assertRaises(FieldKeyNotExistedError):
                    mdl.is_field_none(fk, raise_on_not_exists=True)

    def test_get_field_class_instance(self):
        expected = {
            "Field1": TestBaseModel.TestModel.Field1,
            "Field2": TestBaseModel.TestModel.Field2,
            "Field3": TestBaseModel.TestModel.Field3,
            "Field4": TestBaseModel.TestModel.Field4,
            "Field5": None,
        }

        for fk, fv in expected.items():
            with self.subTest(field_key=fk, expected_value=fv):
                self.assertEqual(TestBaseModel.TestModel.get_field_class_instance(fk), fv)
    # endregion
    # endregion
