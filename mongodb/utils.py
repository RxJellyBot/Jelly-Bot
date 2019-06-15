from pymongo import InsertOne, ReplaceOne
from pymongo.errors import BulkWriteError

from models import OID_KEY


class BulkWriteDataHolder:
    def __init__(self, col, flush_base: int):
        self._col = col
        self._reqs = []
        self._flush_base = flush_base

    @property
    def holding_data(self) -> bool:
        return len(self._reqs) > 0

    def complete(self):
        if self.holding_data:
            try:
                self._col.bulk_write(self._reqs, ordered=False)
            except BulkWriteError as e:
                print("Error occurred during bulk writing:")
                print("\n".join(f"{s['errmsg']}" for s in e.details["writeErrors"]))

    def repsert_single(self, filter_, data):
        """
        :param filter_: Condition for the replacement.
        :param data: Should not contains `_id` field.
        """
        self._reqs.append(ReplaceOne(filter_, data, upsert=True))

    def replace_single(self, data):
        """
        :param data: Must contains `_id` field.
        """
        self._reqs.append(ReplaceOne({OID_KEY: data[OID_KEY]}, data))
