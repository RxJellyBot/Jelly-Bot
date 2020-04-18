from bson import ObjectId
from pymongo.collection import Collection

from ._base import BaseField
from .exceptions import FieldValueInvalid

OID_KEY = "_id"


class ObjectIDField(BaseField):
    def __init__(self, name=None, default=None, readonly=True, allow_none=False, auto_cast=True, stores_uid=False):
        super().__init__(name or OID_KEY, default, allow_none, readonly=readonly,
                         auto_cast=auto_cast, stores_uid=stores_uid)

    def _check_value_valid_not_none_(self, value, *, skip_type_check=False, pass_on_castable=False):
        if not self.allow_none and not ObjectId.is_valid(value):
            raise FieldValueInvalid(self.key, value)

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
        return collection_inst.update_many({self.key: old}, {"$set": {self.key: new}}).acknowledged
