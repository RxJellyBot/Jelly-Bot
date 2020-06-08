from extutils.color import ColorFactory
from models import AutoReplyModuleTagModel
from mongodb.factory.results import GetOutcome
from mongodb.factory.ar_conn import AutoReplyModuleTagManager
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestAutoReplyModuleTagManager"]


class TestAutoReplyModuleTagManager(TestModelMixin, TestDatabaseMixin):
    @staticmethod
    def collections_to_reset():
        return [AutoReplyModuleTagManager]

    @classmethod
    def _insert_5_tags(cls):
        AutoReplyModuleTagManager.get_insert("TAG1", ColorFactory.WHITE)
        AutoReplyModuleTagManager.get_insert("TAG2", ColorFactory.WHITE)
        AutoReplyModuleTagManager.get_insert("TAG3", ColorFactory.WHITE)
        AutoReplyModuleTagManager.get_insert("TAG4", ColorFactory.WHITE)
        AutoReplyModuleTagManager.get_insert("TAG5", ColorFactory.WHITE)

    def test_get_insert_default_color(self):
        expected_mdl = AutoReplyModuleTagModel(Name="TAG", Color=ColorFactory.DEFAULT)

        result = AutoReplyModuleTagManager.get_insert("TAG")

        self.assertEqual(result.outcome, GetOutcome.O_ADDED)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, expected_mdl)

    def test_get_insert_custom_color(self):
        expected_mdl = AutoReplyModuleTagModel(Name="TAG", Color=ColorFactory.WHITE)

        result = AutoReplyModuleTagManager.get_insert("TAG", ColorFactory.WHITE)

        self.assertEqual(result.outcome, GetOutcome.O_ADDED)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, expected_mdl)

    def test_get_insert_existed(self):
        expected_mdl = AutoReplyModuleTagModel(Name="TAG", Color=ColorFactory.WHITE)

        AutoReplyModuleTagManager.get_insert("TAG", ColorFactory.WHITE)
        result = AutoReplyModuleTagManager.get_insert("TAG", ColorFactory.WHITE)

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, expected_mdl)

    def test_search_exact_match(self):
        self._insert_5_tags()

        expected = [AutoReplyModuleTagModel(Name="TAG5", Color=ColorFactory.WHITE)]

        self.assertModelSequenceEqual(list(AutoReplyModuleTagManager.search_tags("TAG5")), expected)

    def test_search_regex(self):
        self._insert_5_tags()

        expected = [
            AutoReplyModuleTagModel(Name="TAG5", Color=ColorFactory.WHITE),
            AutoReplyModuleTagModel(Name="TAG4", Color=ColorFactory.WHITE),
            AutoReplyModuleTagModel(Name="TAG3", Color=ColorFactory.WHITE),
            AutoReplyModuleTagModel(Name="TAG2", Color=ColorFactory.WHITE),
            AutoReplyModuleTagModel(Name="TAG1", Color=ColorFactory.WHITE)
        ]

        self.assertModelSequenceEqual(list(AutoReplyModuleTagManager.search_tags("TAG")), expected)

    def test_get_tag_data(self):
        result = AutoReplyModuleTagManager.get_insert("TAG", ColorFactory.WHITE)

        self.assertEqual(AutoReplyModuleTagManager.get_tag_data(result.model.get_oid()), result.model)
