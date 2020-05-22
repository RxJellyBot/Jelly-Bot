from bson import ObjectId

from tests.base import TestDatabaseMixin
from models import Model
from models.field import ObjectIDField, ArrayField

__all__ = ["TestReplaceUid"]


class ModelForTest(Model):
    IdField = ObjectIDField("o", stores_uid=True)
    IdsField = ArrayField("a", ObjectId, stores_uid=True)


class TestReplaceUid(TestDatabaseMixin):
    OLD = ObjectId()
    NEW = ObjectId()

    def setUpTestCase(self) -> None:
        col = self.get_collection("testcol")
        col.insert_one({"o": TestReplaceUid.OLD, "a": [TestReplaceUid.OLD]})

    def test_replace_oid(self):
        col = self.get_collection("testcol")
        failed = ModelForTest.replace_uid(col, TestReplaceUid.OLD, TestReplaceUid.NEW)

        self.assertEqual([], failed)

        data = col.find_one()
        del data["_id"]
        self.assertEqual({"o": TestReplaceUid.NEW, "a": [TestReplaceUid.NEW]}, data)
