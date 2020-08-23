from datetime import datetime

from bson import ObjectId

from models import AutoReplyModuleModel
from models.exceptions import FieldKeyNotExistError, InvalidModelFieldError
from models.field.exceptions import FieldValueNegativeError
from mongodb.factory.results import WriteOutcome
from mongodb.factory.ar_conn import AutoReplyManager, AutoReplyModuleManager
from tests.base import TestModelMixin

from ._base_ar import TestAutoReplyManagerBase

__all__ = ["TestAutoReplyManagerAdd"]


class TestAutoReplyManagerAdd(TestAutoReplyManagerBase.TestClass, TestModelMixin):
    def _check_model_exists(self, model: AutoReplyModuleModel, *, active_only: bool = True):
        kw = model.keyword.content
        kw_type = model.keyword.content_type

        filter_ = {
            AutoReplyModuleModel.KEY_KW_CONTENT: kw,
            AutoReplyModuleModel.KEY_KW_TYPE: kw_type,
            AutoReplyModuleModel.Active.key: True
        }

        self.assertModelEqual(
            model,
            AutoReplyModuleManager.find_one_casted(filter_))

    def _check_model_not_exists(self, model_args: dict):
        kw = model_args["Keyword"].content
        kw_type = model_args["Keyword"].content_type

        self.assertIsNone(
            AutoReplyModuleManager.find_one_casted({
                AutoReplyModuleModel.KEY_KW_CONTENT: kw,
                AutoReplyModuleModel.KEY_KW_TYPE: kw_type
            }))

    def test_add_single_not_pinned(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_1_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_1())

        self._check_model_exists(self.get_mdl_1())

    def test_add_duplicated_kw_overwrite(self):
        AutoReplyManager.add_conn(**self.get_mdl_1_args())
        result = AutoReplyManager.add_conn(**self.get_mdl_2_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_2())

        self._check_model_exists(self.get_mdl_2())

    def test_add_duplicated_response(self):
        AutoReplyManager.add_conn(**self.get_mdl_1_args())
        result = AutoReplyManager.add_conn(**self.get_mdl_4_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_4())

        self._check_model_exists(self.get_mdl_4())

    def test_add_kw_invalid_sticker_id(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_8_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_KEYWORD)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self._check_model_not_exists(self.get_mdl_8_args())

    def test_add_resp_invalid_sticker_id(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_15_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_RESPONSE)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self._check_model_not_exists(self.get_mdl_15_args())

    def test_add_kw_invalid_image_url(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_9_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_KEYWORD)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self._check_model_not_exists(self.get_mdl_9_args())

    def test_add_invalid_param(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_14_args())

        self.assertEqual(result.outcome, WriteOutcome.X_MODEL_KEY_NOT_EXIST)
        self.assertIsInstance(result.exception, FieldKeyNotExistError)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self._check_model_not_exists(self.get_mdl_14_args())

    def test_add_back_after_del(self):
        # Add one first
        AutoReplyManager.add_conn(**self.get_mdl_1_args())

        # Delete one and test get
        AutoReplyManager.del_conn(self.get_mdl_1().keyword.content, self.channel_oid, self.CREATOR_OID)
        self._check_model_not_exists(self.get_mdl_1_args())

        # Add the same back
        result = AutoReplyManager.add_conn(**self.get_mdl_1_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_1())

        self._check_model_exists(self.get_mdl_1())

    def test_add_inherit_from_active(self):
        kwargs = self.get_mdl_3_args()
        AutoReplyManager.add_conn(**kwargs)

        result = AutoReplyManager.add_conn(**self.get_mdl_2_args())
        # Not using `self.get_mdl_3()` to preserve some OIDs because it will generated on called
        mdl_expected = AutoReplyModuleModel(**kwargs)
        mdl_expected.responses = self.get_mdl_2().responses

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, mdl_expected)

        self._check_model_exists(mdl_expected)

    def test_add_inherit_original_inactive(self):
        AutoReplyManager.add_conn(**self.get_mdl_3_args())
        AutoReplyManager.del_conn(self.get_mdl_3().keyword.content, self.channel_oid, self.CREATOR_OID)

        result = AutoReplyManager.add_conn(**self.get_mdl_2_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_2())

        self._check_model_exists(self.get_mdl_2())

    def test_add_pinned_has_permission(self):
        self.grant_access_pin_permission()

        result = AutoReplyManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_5())

        self._check_model_exists(self.get_mdl_5())

    def test_add_pinned_overwrite_has_permission(self):
        self.grant_access_pin_permission()

        AutoReplyManager.add_conn(**self.get_mdl_5_args())
        result = AutoReplyManager.add_conn(**self.get_mdl_10_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_10())

        self._check_model_exists(self.get_mdl_10())

    def test_add_pinned_no_permission(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self._check_model_not_exists(self.get_mdl_5_args())

    def test_add_pinned_overwrite_no_permission(self):
        self.grant_access_pin_permission()

        AutoReplyManager.add_conn(**self.get_mdl_5_args())
        result = AutoReplyManager.add_conn(**self.get_mdl_11_args())

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self._check_model_exists(self.get_mdl_5())

    def test_add_pinned_overwrite_not_pinned(self):
        self.grant_access_pin_permission()

        AutoReplyManager.add_conn(**self.get_mdl_5_args())
        result = AutoReplyManager.add_conn(**self.get_mdl_6_args())

        self.assertEqual(result.outcome, WriteOutcome.X_PINNED_CONTENT_EXISTED)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self._check_model_exists(self.get_mdl_5())

    def test_add_same_content_different_type(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_12_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_12())

        self._check_model_exists(self.get_mdl_12())

        result = AutoReplyManager.add_conn(**self.get_mdl_13_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, self.get_mdl_13())

        self._check_model_exists(self.get_mdl_13())

    def test_add_negative_cooldown(self):
        result = AutoReplyManager.add_conn(**self.get_mdl_16_args())
        self.assertEqual(result.outcome, WriteOutcome.X_INVALID_MODEL)
        self.assertIsInstance(result.exception, InvalidModelFieldError)
        self.assertIsInstance(result.exception.inner_exception, FieldValueNegativeError)
        self.assertFalse(result.success)
        self.assertIsNone(result.model, self.get_mdl_13())

    def test_add_short_time_overwrite_perma_remove(self):
        AutoReplyManager.add_conn(**self.get_mdl_1_args())
        mdl = AutoReplyManager.add_conn(**self.get_mdl_2_args()).model

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)
        self.assertEqual(AutoReplyModuleManager.find_one(), mdl)

    def test_add_long_time_overwrite_preserve(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        AutoReplyManager.add_conn(**args)

        AutoReplyManager.add_conn(**self.get_mdl_2_args())

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 2)
