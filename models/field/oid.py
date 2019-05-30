from bson import ObjectId

from ._base import BaseField

OID_KEY = "_id"


class ObjectIDField(BaseField):
    def __init__(self, name=OID_KEY, oid: ObjectId = None, readonly=True, allow_none=False):
        super().__init__(name, oid, allow_none, readonly=readonly)

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value) and ObjectId.is_valid(value)

    @classmethod
    def none_obj(cls):
        return ObjectId("000000000000000000000000")

    @property
    def expected_types(self):
        return ObjectId
