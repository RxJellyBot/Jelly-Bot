from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import UpdateResult

from ._base import BaseField

OID_KEY = "_id"


class ObjectIDField(BaseField):
    def __init__(self, name=None, default=None, readonly=True, allow_none=False, auto_cast=True, stores_uid=False):
        super().__init__(name or OID_KEY, default, allow_none, readonly=readonly,
                         auto_cast=auto_cast, stores_uid=stores_uid)

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value) and (self.allow_none or ObjectId.is_valid(value))

    @classmethod
    def none_obj(cls):
        return ObjectId("000000000000000000000000")

    @property
    def expected_types(self):
        return ObjectId

    @property
    def replace_uid_implemented(self) -> bool:
        return True

    def replace_uid(self, collection_inst: Collection, old: ObjectId, new: ObjectId) -> bool:
        return collection_inst.update_many({}, {"$set": {self.key: new}}).acknowledged
