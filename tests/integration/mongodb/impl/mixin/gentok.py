from tests.base import TestDatabaseMixin
from models import Model
from models.field import IntegerField, TextField
from mongodb.factory import BaseCollection, GenerateTokenMixin

__all__ = ["TestGenerateTokenMixin"]


class TestGenerateTokenMixinModel(Model):
    IntF = IntegerField("i", positive_only=True)
    TokenF = TextField("t")


class TestGenerateTokenMixin(TestDatabaseMixin):
    class CollectionTest(GenerateTokenMixin, BaseCollection):
        database_name = "db"
        collection_name = "col"
        model_class = TestGenerateTokenMixinModel

        token_length = 5
        token_key = TestGenerateTokenMixinModel.TokenF.key

    class CollectionTestNoLength(GenerateTokenMixin, BaseCollection):
        database_name = "db"
        collection_name = "col"
        model_class = TestGenerateTokenMixinModel

        token_key = TestGenerateTokenMixinModel.TokenF.key

    class CollectionTestNoKey(GenerateTokenMixin, BaseCollection):
        database_name = "db"
        collection_name = "col"
        model_class = TestGenerateTokenMixinModel

        token_length = 5

    @classmethod
    def setUpTestClass(cls):
        cls.collection = TestGenerateTokenMixin.CollectionTest()

    def test_col_missing_configs(self):
        with self.assertRaises(AttributeError):
            TestGenerateTokenMixin.CollectionTestNoLength()
        with self.assertRaises(AttributeError):
            TestGenerateTokenMixin.CollectionTestNoKey()

    def test_generate_token(self):
        """
        Only testing the length of the token.

        Not testing token regenration on duplicated.
        """
        self.assertEqual(len(self.collection.generate_hex_token()), 5)
