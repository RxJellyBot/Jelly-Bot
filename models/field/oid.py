from bson import ObjectId
from pymongo.collection import Collection

from ._base import BaseField
from .exceptions import FieldValueInvalid

OID_KEY = "_id"


class ObjectIDField(BaseField):
    def __init__(self, key=None, **kwargs):
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False
        if "readonly" not in kwargs:
            kwargs["readonly"] = True

        super().__init__(key or OID_KEY, **kwargs)

    def _check_value_valid_not_none_(self, value):
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
