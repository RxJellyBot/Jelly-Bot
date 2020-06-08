from datetime import datetime

from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import Platform
from models import AutoReplyModuleModel
from mongodb.factory.results import WriteOutcome
from mongodb.factory import ChannelManager
from mongodb.factory.ar_conn import AutoReplyManager, AutoReplyModuleManager
from tests.base import TestTimeComparisonMixin, TestModelMixin

from ._base_ar import TestAutoReplyManagerBase

__all__ = ["TestAutoReplyManagerDelete"]


class TestAutoReplyManagerDelete(TestAutoReplyManagerBase.TestClass, TestTimeComparisonMixin, TestModelMixin):
    def _check_model_exists(self, model: AutoReplyModuleModel):
        kw = model.keyword.content
        kw_type = model.keyword.content_type

        self.assertModelEqual(
            model,
            AutoReplyModuleManager.find_one_casted({
                AutoReplyModuleModel.KEY_KW_CONTENT: kw,
                AutoReplyModuleModel.KEY_KW_TYPE: kw_type
            }, parse_cls=AutoReplyModuleModel))

    def _check_model_not_exists(self, model_args: dict):
        kw = model_args["Keyword"].content
        kw_type = model_args["Keyword"].content_type

        self.assertIsNone(
            AutoReplyModuleManager.find_one_casted({
                AutoReplyModuleModel.KEY_KW_CONTENT: kw,
                AutoReplyModuleModel.KEY_KW_TYPE: kw_type
            }, parse_cls=AutoReplyModuleModel))

    def test_del_short_time_overwrite_perma_remove(self):
        AutoReplyManager.add_conn(**self.get_mdl_1_args())

        AutoReplyManager.del_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.get_mdl_1().creator_oid)

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 0)

    def test_del_long_time_overwrite_preserve(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        AutoReplyManager.add_conn(**args)

        AutoReplyManager.del_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.get_mdl_1().creator_oid)

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)

    def test_del_pinned_has_permission(self):
        self.grant_access_pin_permission()

        AutoReplyManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            AutoReplyManager.del_conn(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_oid, self.get_mdl_5().creator_oid),
            WriteOutcome.O_DATA_UPDATED)

        self._check_model_not_exists(self.get_mdl_5_args())

    def test_del_pinned_no_permission(self):
        self.grant_access_pin_permission()
        AutoReplyManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            AutoReplyManager.del_conn(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_oid, self.CREATOR_OID_2),
            WriteOutcome.X_INSUFFICIENT_PERMISSION)

        self._check_model_exists(self.get_mdl_5())

    def test_del_mark_remover_and_time(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        AutoReplyManager.add_conn(**args)

        removed_time = now_utc_aware()
        AutoReplyManager.del_conn(self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.CREATOR_OID_2)

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)
        mdl = AutoReplyModuleModel(**AutoReplyModuleManager.find_one(), from_db=True)
        self.assertEqual(mdl.remover_oid, self.CREATOR_OID_2)
        self.assertTimeDifferenceLessEqual(mdl.removed_at, removed_time, 1)

    def test_del_channel_not_found(self):
        self.channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id
        AutoReplyManager.add_conn(**self.get_mdl_5_args())

        result = AutoReplyManager.del_conn(self.get_mdl_5().keyword.content, ObjectId(), self.CREATOR_OID_2)
        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)

    def test_del_keyword_not_found(self):
        AutoReplyManager.add_conn(**self.get_mdl_5_args())

        result = AutoReplyManager.del_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_5().channel_oid, self.CREATOR_OID_2)
        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)
