from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import ExtraContentType
from models import ExtraContentModel
from mongodb.factory.exctnt import ExtraContentManager
from mongodb.factory.results import WriteOutcome
from tests.base import TestDatabaseMixin, TestModelMixin, TestTimeComparisonMixin
from strnames.msghandle import ToSiteReason

__all__ = ["TestExtraContentManager"]


class TestExtraContentManager(TestModelMixin, TestTimeComparisonMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()

    @staticmethod
    def collections_to_reset():
        return [ExtraContentManager]

    def test_rec_extra_message(self):
        rec_time = now_utc_aware(for_mongo=True)
        result = ExtraContentManager.record_extra_message(self.CHANNEL_OID, [(ToSiteReason.FORCED_ONSITE, "A")], "T")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(
            result.model,
            ExtraContentModel(Type=ExtraContentType.EXTRA_MESSAGE, Title="T",
                              Content=[(str(ToSiteReason.FORCED_ONSITE), "A")],
                              Timestamp=result.model.timestamp, ChannelOid=self.CHANNEL_OID))
        self.assertTimeDifferenceLessEqual(result.model.timestamp, rec_time, 2)

    def test_rec_no_title(self):
        rec_time = now_utc_aware(for_mongo=True)
        result = ExtraContentManager.record_content(ExtraContentType.EXTRA_MESSAGE, self.CHANNEL_OID,
                                                    [(str(ToSiteReason.FORCED_ONSITE), "A")], "T")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(
            result.model,
            ExtraContentModel(Type=ExtraContentType.EXTRA_MESSAGE, Title="T",
                              Content=[(str(ToSiteReason.FORCED_ONSITE), "A")],
                              Timestamp=result.model.timestamp, ChannelOid=self.CHANNEL_OID))
        self.assertTimeDifferenceLessEqual(result.model.timestamp, rec_time, 2)

    def test_rec_no_content(self):
        result = ExtraContentManager.record_content(ExtraContentType.EXTRA_MESSAGE, self.CHANNEL_OID, [], "T")

        self.assertEqual(result.outcome, WriteOutcome.X_EMPTY_CONTENT)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

    def test_rec_content_pure_text(self):
        rec_time = now_utc_aware(for_mongo=True)
        result = ExtraContentManager.record_content(ExtraContentType.PURE_TEXT, self.CHANNEL_OID, "ABCDE", "T")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(
            result.model,
            ExtraContentModel(Type=ExtraContentType.PURE_TEXT, Title="T", Content="ABCDE",
                              Timestamp=result.model.timestamp, ChannelOid=self.CHANNEL_OID))
        self.assertTimeDifferenceLessEqual(result.model.timestamp, rec_time, 2)

    def test_rec_content_ex_message(self):
        rec_time = now_utc_aware(for_mongo=True)
        result = ExtraContentManager.record_content(ExtraContentType.EXTRA_MESSAGE, self.CHANNEL_OID,
                                                    [(str(ToSiteReason.FORCED_ONSITE), "A")], "T")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(
            result.model,
            ExtraContentModel(Type=ExtraContentType.EXTRA_MESSAGE, Title="T",
                              Content=[(str(ToSiteReason.FORCED_ONSITE), "A")],
                              Timestamp=result.model.timestamp, ChannelOid=self.CHANNEL_OID))
        self.assertTimeDifferenceLessEqual(result.model.timestamp, rec_time, 2)

    def test_rec_ar_search(self):
        ar_oids = [ObjectId(), ObjectId()]

        rec_time = now_utc_aware(for_mongo=True)
        result = ExtraContentManager.record_content(ExtraContentType.AUTO_REPLY_SEARCH, self.CHANNEL_OID, ar_oids, "T")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(
            result.model,
            ExtraContentModel(Type=ExtraContentType.AUTO_REPLY_SEARCH, Title="T", Content=ar_oids,
                              Timestamp=result.model.timestamp, ChannelOid=self.CHANNEL_OID))
        self.assertTimeDifferenceLessEqual(result.model.timestamp, rec_time, 2)

    def test_get_content(self):
        result = ExtraContentManager.record_content(ExtraContentType.PURE_TEXT, self.CHANNEL_OID, "ABCDE", "T")

        self.assertEqual(ExtraContentManager.get_content(result.model_id), result.model)
