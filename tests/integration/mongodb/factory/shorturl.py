import os

from bson import ObjectId

from models import ShortUrlRecordModel
from mongodb.factory import ShortUrlDataManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestShortUrlDataManager"]


class TestShortUrlDataManager(TestModelMixin, TestDatabaseMixin):
    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [ShortUrlDataManager]

    def test_check_service(self):
        self.assertTrue(ShortUrlDataManager.check_service())

    def test_check_service_falsy(self):
        temp = os.environ.get("SERVICE_SHORT_URL")
        os.environ["SERVICE_SHORT_URL"] = "abc"
        self.assertFalse(ShortUrlDataManager.check_service())
        os.environ["SERVICE_SHORT_URL"] = temp

    def test_generate_code(self):
        self.assertTrue(
            all(c in ShortUrlDataManager.AVAILABLE_CHARACTERS for c in ShortUrlDataManager.generate_code())
        )

    def test_create_record(self):
        result = ShortUrlDataManager.create_record("https://google.com", self.USER_OID)

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertModelEqual(
            result.model,
            ShortUrlRecordModel(Code=result.model.code, Target="https://google.com", CreatorOid=self.USER_OID)
        )

    def test_create_record_non_url(self):
        result = ShortUrlDataManager.create_record("abc", self.USER_OID)

        self.assertEqual(result.outcome, WriteOutcome.X_INVALID_URL)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

    def test_get_target(self):
        code = ShortUrlDataManager.generate_code()
        ShortUrlDataManager.insert_one_model(
            ShortUrlRecordModel(Code=code, Target="https://google.com", CreatorOid=self.USER_OID)
        )

        self.assertEqual(ShortUrlDataManager.get_target(code), "https://google.com")

    def test_get_target_no_data(self):
        self.assertIsNone(ShortUrlDataManager.get_target(ShortUrlDataManager.generate_code()))

    def test_get_target_miss(self):
        ShortUrlDataManager.insert_one_model(
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://google.com",
                                CreatorOid=self.USER_OID)
        )

        self.assertIsNone(ShortUrlDataManager.get_target(ShortUrlDataManager.generate_code()))

    def test_get_record(self):
        code = ShortUrlDataManager.generate_code()
        mdl = ShortUrlRecordModel(Code=code, Target="https://google.com", CreatorOid=self.USER_OID)
        ShortUrlDataManager.insert_one_model(mdl)

        self.assertEqual(ShortUrlDataManager.get_record(code), mdl)

    def test_get_record_no_data(self):
        self.assertIsNone(ShortUrlDataManager.get_record(ShortUrlDataManager.generate_code()))

    def test_get_record_miss(self):
        ShortUrlDataManager.insert_one_model(
            ShortUrlRecordModel(
                Code=ShortUrlDataManager.generate_code(), Target="https://google.com",
                CreatorOid=self.USER_OID
            )
        )

        self.assertIsNone(ShortUrlDataManager.get_record(ShortUrlDataManager.generate_code()))

    def test_get_user_record(self):
        mdls = [
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://google.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://facebook.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://yahoo.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://python.org",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://imgur.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://google.com",
                                CreatorOid=self.USER_OID_2)
        ]
        ShortUrlDataManager.insert_many(mdls)

        self.assertEqual(list(ShortUrlDataManager.get_user_record(self.USER_OID)), mdls[0:5])

    def test_get_user_record_no_data(self):
        self.assertEqual(list(ShortUrlDataManager.get_user_record(self.USER_OID)), [])

    def test_get_user_record_miss(self):
        mdls = [
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://google.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://facebook.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://yahoo.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://python.org",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://imgur.com",
                                CreatorOid=self.USER_OID),
            ShortUrlRecordModel(Code=ShortUrlDataManager.generate_code(), Target="https://google.com",
                                CreatorOid=self.USER_OID_2)
        ]
        ShortUrlDataManager.insert_many(mdls)

        self.assertEqual(list(ShortUrlDataManager.get_user_record(ObjectId())), [])

    def test_update_target(self):
        code = ShortUrlDataManager.generate_code()
        ShortUrlDataManager.insert_one_model(
            ShortUrlRecordModel(Code=code, Target="https://google.com", CreatorOid=self.USER_OID)
        )

        self.assertTrue(ShortUrlDataManager.update_target(self.USER_OID, code, "https://facebook.com"))
        self.assertModelEqual(
            ShortUrlDataManager.find_one_casted(parse_cls=ShortUrlRecordModel),
            ShortUrlRecordModel(Code=code, Target="https://facebook.com", CreatorOid=self.USER_OID)
        )

    def test_update_target_no_data(self):
        self.assertFalse(
            ShortUrlDataManager.update_target(
                self.USER_OID, ShortUrlDataManager.generate_code(), "https://facebook.com")
        )

        self.assertEqual(ShortUrlDataManager.count_documents({}), 0)

    def test_update_target_invalid_url(self):
        code = ShortUrlDataManager.generate_code()
        mdl = ShortUrlRecordModel(Code=code, Target="https://google.com", CreatorOid=self.USER_OID)
        ShortUrlDataManager.insert_one_model(mdl)

        self.assertFalse(ShortUrlDataManager.update_target(self.USER_OID, code, "abc"))
        self.assertEqual(ShortUrlDataManager.find_one_casted(parse_cls=ShortUrlRecordModel), mdl)
