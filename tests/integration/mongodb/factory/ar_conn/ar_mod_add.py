from datetime import datetime

from bson import ObjectId

from models import AutoReplyModuleModel
from models.exceptions import FieldKeyNotExistError, InvalidModelFieldError
from models.field.exceptions import FieldValueNegativeError
from mongodb.factory.results import WriteOutcome
from mongodb.factory.ar_conn import AutoReplyModuleManager
from tests.base import TestModelMixin

from ._base_ar_mod import TestAutoReplyModuleManagerBase

__all__ = ["TestAutoReplyModuleManagerAdd"]


class TestAutoReplyModuleManagerAdd(TestModelMixin, TestAutoReplyModuleManagerBase.TestClass):
    def test_add_single_not_pinned(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_1_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_1())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_1()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_duplicated_kw_overwrite(self):
        AutoReplyModuleManager.add_conn(**self.get_mdl_1_args())
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_2_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_2())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_2().keyword.content, self.get_mdl_2().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_2()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_duplicated_response(self):
        AutoReplyModuleManager.add_conn(**self.get_mdl_1_args())
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_4_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_4())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_4().keyword.content, self.get_mdl_4().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_4()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_kw_invalid_sticker_id(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_8_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_KEYWORD)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_8_args()["Keyword"].content, self.get_mdl_9_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_resp_invalid_sticker_id(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_15_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_RESPONSE)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_15_args()["Keyword"].content, self.get_mdl_15_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_kw_invalid_image_url(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_9_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_KEYWORD)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_9_args()["Keyword"].content, self.get_mdl_9_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_invalid_param(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_14_args())

        self.assertEqual(result.outcome, WriteOutcome.X_MODEL_KEY_NOT_EXIST)
        self.assertIsInstance(result.exception, FieldKeyNotExistError)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_14_args()["Keyword"].content, self.get_mdl_14_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_back_after_del(self):
        # Add one first
        AutoReplyModuleManager.add_conn(**self.get_mdl_1_args())

        # Delete one and test get
        AutoReplyModuleManager.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.channel_oid, self.CREATOR_OID)
        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.channel_oid)
        self.assertIsNone(mdl)

        # Add the same back
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_1_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_1())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_1()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_inherit_from_active(self):
        kwargs = self.get_mdl_3_args()
        AutoReplyModuleManager.add_conn(**kwargs)

        result = AutoReplyModuleManager.add_conn(**self.get_mdl_2_args())
        # Not using `self.get_mdl_3()` to preserve some OIDs because it will generated on called
        mdl_expected = AutoReplyModuleModel(**kwargs)
        mdl_expected.responses = self.get_mdl_2().responses

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, mdl_expected)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_3().keyword.content, self.get_mdl_3().keyword.content_type, self.channel_oid)
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_inherit_original_inactive(self):
        AutoReplyModuleManager.add_conn(**self.get_mdl_3_args())
        AutoReplyModuleManager.module_mark_inactive(
            self.get_mdl_3().keyword.content, self.channel_oid, self.CREATOR_OID)

        result = AutoReplyModuleManager.add_conn(**self.get_mdl_2_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_2())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_2().keyword.content, self.get_mdl_2().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_2()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_pinned_has_permission(self):
        self.grant_access_pin_permission()

        result = AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_5())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_5()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_pinned_overwrite_has_permission(self):
        self.grant_access_pin_permission()

        AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_10_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_10())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_10().keyword.content, self.get_mdl_10().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_10()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_pinned_no_permission(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_pinned_overwrite_no_permission(self):
        self.grant_access_pin_permission()

        AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_11_args())

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_11().keyword.content, self.get_mdl_11().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_5()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_pinned_overwrite_not_pinned(self):
        self.grant_access_pin_permission()

        AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_6_args())

        self.assertEqual(result.outcome, WriteOutcome.X_PINNED_CONTENT_EXISTED)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_6().keyword.content, self.get_mdl_6().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_5()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_same_content_different_type(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_12_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_12())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_12().keyword.content, self.get_mdl_12().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_12()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

        result = AutoReplyModuleManager.add_conn(**self.get_mdl_13_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_13())

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_13().keyword.content, self.get_mdl_13().keyword.content_type, self.channel_oid)
        mdl_expected = self.get_mdl_13()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_add_negative_cooldown(self):
        result = AutoReplyModuleManager.add_conn(**self.get_mdl_16_args())
        self.assertEqual(result.outcome, WriteOutcome.X_INVALID_MODEL)
        self.assertIsInstance(result.exception, InvalidModelFieldError)
        self.assertIsInstance(result.exception.inner_exception, FieldValueNegativeError)
        self.assertFalse(result.success)
        self.assertIsNone(result.model, self.get_mdl_13())

    def test_add_short_time_overwrite_perma_remove(self):
        AutoReplyModuleManager.add_conn(**self.get_mdl_1_args())
        mdl = AutoReplyModuleManager.add_conn(**self.get_mdl_2_args()).model

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)
        self.assertEqual(AutoReplyModuleManager.find_one(), mdl)

    def test_add_long_time_overwrite_preserve(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        AutoReplyModuleManager.add_conn(**args)

        AutoReplyModuleManager.add_conn(**self.get_mdl_2_args())

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 2)
