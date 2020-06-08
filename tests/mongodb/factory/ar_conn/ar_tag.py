from bson import ObjectId

from extutils.color import ColorFactory
from flags import AutoReplyContentType
from models import AutoReplyModuleTagModel, AutoReplyContentModel
from mongodb.factory.results import GetOutcome
from mongodb.factory.ar_conn import AutoReplyManager, AutoReplyModuleManager
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestAutoReplyManagerTag"]


class TestAutoReplyManagerTag(TestModelMixin, TestDatabaseMixin):
    @staticmethod
    def collections_to_reset():
        return [AutoReplyManager, AutoReplyModuleManager]

    @classmethod
    def _insert_5_tags(cls, *, add_related_ar_module: bool = False):
        t1 = AutoReplyManager.tag_get_insert("TAG1", ColorFactory.WHITE).model.id
        t2 = AutoReplyManager.tag_get_insert("TAG2", ColorFactory.WHITE).model.id
        t3 = AutoReplyManager.tag_get_insert("TAG3", ColorFactory.WHITE).model.id
        t4 = AutoReplyManager.tag_get_insert("TAG4", ColorFactory.WHITE).model.id
        t5 = AutoReplyManager.tag_get_insert("TAG5", ColorFactory.WHITE).model.id

        if add_related_ar_module:
            channel_oid = ObjectId()
            creator_oid = ObjectId()

            AutoReplyModuleManager.add_conn(
                Keyword=AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
                Responses=[
                    AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)],
                ChannelOid=channel_oid, CreatorOid=creator_oid, TagIds=[t1, t2])
            AutoReplyModuleManager.add_conn(
                Keyword=AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT),
                Responses=[
                    AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)],
                ChannelOid=channel_oid, CreatorOid=creator_oid, TagIds=[t1, t3])
            AutoReplyModuleManager.add_conn(
                Keyword=AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT),
                Responses=[
                    AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
                ChannelOid=channel_oid, CreatorOid=creator_oid, TagIds=[t1, t4, t5])
            AutoReplyModuleManager.add_conn(
                Keyword=AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT),
                Responses=[
                    AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)],
                ChannelOid=channel_oid, CreatorOid=creator_oid, TagIds=[t2, t4])
            AutoReplyModuleManager.add_conn(
                Keyword=AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT),
                Responses=[
                    AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)],
                ChannelOid=channel_oid, CreatorOid=creator_oid, TagIds=[t3, t5])
            AutoReplyModuleManager.add_conn(
                Keyword=AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT),
                Responses=[
                    AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT)],
                ChannelOid=channel_oid, CreatorOid=creator_oid, TagIds=[t1, t2])

    def test_get_insert_default_color(self):
        expected_mdl = AutoReplyModuleTagModel(Name="TAG", Color=ColorFactory.DEFAULT)

        result = AutoReplyManager.tag_get_insert("TAG")

        self.assertEqual(result.outcome, GetOutcome.O_ADDED)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, expected_mdl)

    def test_get_insert_custom_color(self):
        expected_mdl = AutoReplyModuleTagModel(Name="TAG", Color=ColorFactory.WHITE)

        result = AutoReplyManager.tag_get_insert("TAG", ColorFactory.WHITE)

        self.assertEqual(result.outcome, GetOutcome.O_ADDED)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, expected_mdl)

    def test_get_insert_existed(self):
        expected_mdl = AutoReplyModuleTagModel(Name="TAG", Color=ColorFactory.WHITE)

        AutoReplyManager.tag_get_insert("TAG", ColorFactory.WHITE)
        result = AutoReplyManager.tag_get_insert("TAG", ColorFactory.WHITE)

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, expected_mdl)

    def test_get_score_no_tag(self):
        self.assertEqual([], AutoReplyManager.get_popularity_scores("TAG"))

    def test_get_score_has_tag(self):
        self._insert_5_tags(add_related_ar_module=True)
        self.assertTrue(len(AutoReplyManager.get_popularity_scores("TAG")) > 0)

    def test_get_score_limit_count(self):
        self._insert_5_tags(add_related_ar_module=True)
        self.assertTrue(len(AutoReplyManager.get_popularity_scores("TAG", 3)), 3)
