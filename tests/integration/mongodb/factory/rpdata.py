from bson import ObjectId

from models import PendingRepairDataModel, OID_KEY
from mongodb.factory import MONGO_CLIENT, SINGLE_DB_NAME, BaseCollection, PendingRepairDataManager

from tests.base import TestDatabaseMixin

__all__ = ["TestPendingRepairDataManager"]


class TestCollection(BaseCollection):
    database_name = "testdb"
    collection_name = "testcol"
    model_class = PendingRepairDataModel


_col_inst = TestCollection()


class TestPendingRepairDataManager(TestDatabaseMixin):
    def test_new_bulk_data_holder(self):
        holder = PendingRepairDataManager.new_bulk_holder(_col_inst)

        missing_data = [
            ({OID_KEY: ObjectId(), "c": "d"}, ["a", "b"]),
            ({OID_KEY: ObjectId(), "a": "e", "c": "d"}, ["b"])
        ]

        for data, missing in missing_data:
            holder.repsert_single(
                {f"{PendingRepairDataModel.Data.key}.{OID_KEY}": data[OID_KEY]},
                PendingRepairDataModel(Data=data, MissingKeys=missing))

        col = MONGO_CLIENT.get_database(SINGLE_DB_NAME).get_collection("pdrp.testdb.testcol")
        col.delete_many({})

        self.assertEqual(len(holder.complete()), 2)
        self.assertEqual(col.count_documents({}), 2, list(col.find()))
