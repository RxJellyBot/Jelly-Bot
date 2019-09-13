from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from models import OID_KEY

from .logger import logger


class BulkWriteDataHolder:
    def __init__(self, col, flush_base: int):
        self._col = col
        self._reqs = []
        self._flush_base = flush_base

    @property
    def holding_data(self) -> bool:
        return self.holded_count > 0

    @property
    def holded_count(self) -> int:
        return len(self._reqs)

    def complete(self):
        if self.holding_data:
            try:
                return [oid for idx, oid in self._col.bulk_write(self._reqs, ordered=False).upserted_ids.items()]
            except BulkWriteError as e:
                logger.logger.exception("\n".join(f"{s['errmsg']}" for s in e.details["writeErrors"]))
                return e.details["writeErrors"]

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
