from datetime import datetime

from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import Platform
from models import AutoReplyModuleModel
from mongodb.factory import ChannelManager
from mongodb.factory.ar_conn import AutoReplyModuleManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestModelMixin, TestTimeComparisonMixin

from ._base_ar_mod import TestAutoReplyModuleManagerBase

__all__ = ["TestAutoReplyModuleManagerDelete"]


class TestAutoReplyModuleManagerDelete(TestModelMixin, TestTimeComparisonMixin,
                                       TestAutoReplyModuleManagerBase.TestClass):
    def test_del_short_time_overwrite_perma_remove(self):
        AutoReplyModuleManager.add_conn(**self.get_mdl_1_args())

        AutoReplyModuleManager.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.get_mdl_1().creator_oid)

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 0)

    def test_del_long_time_overwrite_preserve(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        AutoReplyModuleManager.add_conn(**args)

        AutoReplyModuleManager.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.get_mdl_1().creator_oid)

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)

    def test_del_pinned_has_permission(self):
        self.grant_access_pin_permission()

        AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            AutoReplyModuleManager.module_mark_inactive(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_oid, self.get_mdl_5().creator_oid),
            WriteOutcome.O_DATA_UPDATED)

        self.assertIsNone(
            AutoReplyModuleManager.get_conn(
                self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.get_mdl_5().channel_oid))

    def test_del_pinned_no_permission(self):
        self.grant_access_pin_permission()
        AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            AutoReplyModuleManager.module_mark_inactive(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_oid, self.CREATOR_OID_2),
            WriteOutcome.X_INSUFFICIENT_PERMISSION)

        mdl = AutoReplyModuleManager.get_conn(
            self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.get_mdl_5().channel_oid)
        mdl_expected = self.get_mdl_5()
        mdl_expected.called_count = 1
        self.assertModelEqual(mdl, mdl_expected)

    def test_del_mark_remover_and_time(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        AutoReplyModuleManager.add_conn(**args)

        removed_time = now_utc_aware()
        AutoReplyModuleManager.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.CREATOR_OID_2)

        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)
        mdl = AutoReplyModuleModel(**AutoReplyModuleManager.find_one(), from_db=True)
        self.assertEqual(mdl.remover_oid, self.CREATOR_OID_2)
        self.assertTimeDifferenceLessEqual(mdl.removed_at, removed_time, 1)

    def test_del_channel_not_found(self):
        self.channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id
        AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())

        result = AutoReplyModuleManager.module_mark_inactive(
            self.get_mdl_5().keyword.content, ObjectId(), self.CREATOR_OID_2)
        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)

    def test_del_keyword_not_found(self):
        AutoReplyModuleManager.add_conn(**self.get_mdl_5_args())

        result = AutoReplyModuleManager.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_5().channel_oid, self.CREATOR_OID_2)
        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)
