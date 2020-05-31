import time
from datetime import datetime

from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import AutoReplyContentType, Platform
from models import AutoReplyContentModel, AutoReplyModuleModel
from models.ar import UniqueKeywordCountEntry
from mongodb.factory.results import WriteOutcome
from mongodb.factory import ChannelManager

from ._base import TestArModuleManagerBase

__all__ = ["TestArModuleManagerDelete"]


class TestArModuleManagerDelete(TestArModuleManagerBase):
    def test_del_short_time_overwrite_perma_remove(self):
        self.inst.add_conn(**self.get_mdl_1_args())

        self.inst.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.get_mdl_1().creator_oid)

        self.assertEqual(self.inst.count_documents({}), 0)

    def test_del_long_time_overwrite_preserve(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        self.inst.add_conn(**args)

        self.inst.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.get_mdl_1().creator_oid)

        self.assertEqual(self.inst.count_documents({}), 1)

    def test_del_pinned_has_permission(self):
        self.grant_access_pin_permission()

        self.inst.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            self.inst.module_mark_inactive(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_oid, self.get_mdl_5().creator_oid),
            WriteOutcome.O_DATA_UPDATED)

        self.assertIsNone(
            self.inst.get_conn(
                self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.get_mdl_5().channel_oid))

    def test_del_pinned_no_permission(self):
        self.grant_access_pin_permission()
        self.inst.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            self.inst.module_mark_inactive(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_oid, self.CREATOR_OID_2),
            WriteOutcome.X_INSUFFICIENT_PERMISSION)

        mdl = self.inst.get_conn(
            self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.get_mdl_5().channel_oid)
        mdl.clear_oid()
        mdl_expected = self.get_mdl_5()
        mdl_expected.called_count = 1
        self.assertEqual(mdl, mdl_expected)

    def test_del_mark_remover_and_time(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        self.inst.add_conn(**args)

        removed_time = now_utc_aware()
        self.inst.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_oid, self.CREATOR_OID_2)

        self.assertEqual(self.inst.count_documents({}), 1)
        mdl = AutoReplyModuleModel(**self.inst.find_one(), from_db=True)
        self.assertEqual(mdl.remover_oid, self.CREATOR_OID_2)
        self.assertTimeDifferenceLessEqual(mdl.removed_at, removed_time, 1)

    def test_del_channel_not_found(self):
        self.channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id
        self.inst.add_conn(**self.get_mdl_5_args())

        result = self.inst.module_mark_inactive(self.get_mdl_5().keyword.content, ObjectId(), self.CREATOR_OID_2)
        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)

    def test_del_keyword_not_found(self):
        self.inst.add_conn(**self.get_mdl_5_args())

        result = self.inst.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_5().channel_oid, self.CREATOR_OID_2)
        self.assertEqual(result, WriteOutcome.X_NOT_FOUND)

    def test_get_count_call(self):
        mdl = self.inst.add_conn(**self.get_mdl_1_args()).model
        self.assertEqual(mdl.called_count, 0)

        mdl = self.inst.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.get_mdl_1().channel_oid,
            update_count_async=False)
        self.assertEqual(mdl.called_count, 1)

        mdl = self.inst.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.get_mdl_1().channel_oid,
            update_count_async=False)
        self.assertEqual(mdl.called_count, 2)

        mdl = self.inst.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.get_mdl_1().channel_oid,
            update_count_async=False)
        self.assertEqual(mdl.called_count, 3)

    def test_get_after_add_multi(self):
        self.inst.add_conn(**self.get_mdl_1_args())
        self.inst.add_conn(**self.get_mdl_4_args())
        self.inst.add_conn(**self.get_mdl_6_args())

        mdl = self.inst.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.get_mdl_1().channel_oid)
        mdl.clear_oid()
        mdl_expected = self.get_mdl_1()
        mdl_expected.called_count = 1
        self.assertEqual(mdl, mdl_expected)

        mdl = self.inst.get_conn(
            self.get_mdl_4().keyword.content, self.get_mdl_4().keyword.content_type, self.get_mdl_4().channel_oid)
        mdl.clear_oid()
        mdl_expected = self.get_mdl_4()
        mdl_expected.called_count = 1
        self.assertEqual(mdl, mdl_expected)

        mdl = self.inst.get_conn(
            self.get_mdl_6().keyword.content, self.get_mdl_6().keyword.content_type, self.get_mdl_6().channel_oid)
        mdl.clear_oid()
        mdl_expected = self.get_mdl_6()
        mdl_expected.called_count = 1
        self.assertEqual(mdl, mdl_expected)

    def test_get_on_cooldown(self):
        self.inst.add_conn(**self.get_mdl_3_args())
        # Call once to record last used time
        self.inst.get_conn(
            self.get_mdl_3().keyword.content, self.get_mdl_3().keyword.content_type, self.get_mdl_3().channel_oid)

        self.assertIsNone(
            self.inst.get_conn(
                self.get_mdl_3().keyword.content, self.get_mdl_3().keyword.content_type, self.get_mdl_3().channel_oid))

    def test_get_after_cooldown(self):
        self.inst.add_conn(**self.get_mdl_3_args())
        # Call once to record last used time
        self.inst.get_conn(
            self.get_mdl_3().keyword.content, self.get_mdl_3().keyword.content_type, self.get_mdl_3().channel_oid)

        time.sleep(1.3)  # Cooldown of model #3 is 1 sec
        self.assertIsNotNone(
            self.inst.get_conn(
                self.get_mdl_3().keyword.content, self.get_mdl_3().keyword.content_type, self.get_mdl_3().channel_oid))

    def test_get_list_by_keyword_including_inactive(self):
        expected_oids = self._add_call_module_kw_a()

        for idx, actual_mdl in enumerate(self.inst.get_conn_list(self.channel_oid, "A", active_only=False)):
            with self.subTest(expected=expected_oids[idx], actual=actual_mdl):
                self.assertEqual(expected_oids[idx], actual_mdl.id)

    def test_get_list_by_keyword_active_only(self):
        expected_oids = self._add_call_module_kw_a()[2:]

        for idx, actual_mdl in enumerate(self.inst.get_conn_list(self.channel_oid, "A")):
            with self.subTest(expected=expected_oids[idx], actual=actual_mdl):
                self.assertEqual(expected_oids[idx], actual_mdl.id)

    def test_get_list_by_oids(self):
        mdl_oids = self._add_call_module_kw_a()

        expected_kw_resp = (
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)]),
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)]),
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)])
        )

        for mdl, kw_resp in zip(self.inst.get_conn_list_oids(mdl_oids), expected_kw_resp):
            kw, resp = kw_resp
            self.assertEqual(mdl.keyword, kw)
            self.assertEqual(mdl.responses, resp)

    def test_stats_module_count_length_limited(self):
        self._add_call_module_kw_a()

        expected_kw_resp = (
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)]),
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)]),
        )

        # Not using `zip()` to ensure that exceptions will be raised if len(actual) > len(expected)
        # which means the tests is not completed
        for idx, mdl in enumerate(self.inst.get_module_count_stats(self.channel_oid, 2)):
            kw, resp = expected_kw_resp[idx]
            self.assertEqual(kw, mdl.keyword)
            self.assertEqual(resp, mdl.responses)

    def test_stats_module_count_length_overlimit(self):
        self._add_call_module_kw_a()

        expected_kw_resp = (
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)]),
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)]),
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)]),
        )

        for idx, mdl in enumerate(self.inst.get_module_count_stats(self.channel_oid, 5)):
            kw, resp = expected_kw_resp[idx]
            self.assertEqual(kw, mdl.keyword)
            self.assertEqual(resp, mdl.responses)

    def test_stats_module_count_length_no_limit(self):
        self._add_call_module_kw_a()

        expected_kw_resp = (
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)]),
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)]),
            (AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
             [AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)]),
        )

        for idx, mdl in enumerate(self.inst.get_module_count_stats(self.channel_oid)):
            kw, resp = expected_kw_resp[idx]
            self.assertEqual(kw, mdl.keyword)
            self.assertEqual(resp, mdl.responses)

    def test_stats_unique_count_length_limited(self):
        self._add_call_module_multi()

        expected = [
            UniqueKeywordCountEntry("B", AutoReplyContentType.TEXT, 9, 1, "1"),
            UniqueKeywordCountEntry("A", AutoReplyContentType.TEXT, 7, 3, "2"),
            UniqueKeywordCountEntry("C", AutoReplyContentType.TEXT, 0, 2, "3")
        ]

        result = self.inst.get_unique_keyword_count_stats(self.channel_oid, 3)
        self.assertEqual(result.limit, 3)
        self.assertEqual(result.data, expected)

    def test_stats_unique_count_length_overlimit(self):
        self._add_call_module_multi()

        expected = [
            UniqueKeywordCountEntry("B", AutoReplyContentType.TEXT, 9, 1, "1"),
            UniqueKeywordCountEntry("A", AutoReplyContentType.TEXT, 7, 3, "2"),
            UniqueKeywordCountEntry("C", AutoReplyContentType.TEXT, 0, 2, "T3"),
            UniqueKeywordCountEntry("D", AutoReplyContentType.TEXT, 0, 1, "T3")
        ]

        result = self.inst.get_unique_keyword_count_stats(self.channel_oid, 5)
        self.assertEqual(result.limit, 5)
        self.assertEqual(result.data, expected)

    def test_stats_unique_count_length_no_limit(self):
        self._add_call_module_multi()

        expected = [
            UniqueKeywordCountEntry("B", AutoReplyContentType.TEXT, 9, 1, "1"),
            UniqueKeywordCountEntry("A", AutoReplyContentType.TEXT, 7, 3, "2"),
            UniqueKeywordCountEntry("C", AutoReplyContentType.TEXT, 0, 2, "T3"),
            UniqueKeywordCountEntry("D", AutoReplyContentType.TEXT, 0, 1, "T3")
        ]

        result = self.inst.get_unique_keyword_count_stats(self.channel_oid)
        self.assertIsNone(result.limit)
        self.assertEqual(result.data, expected)
