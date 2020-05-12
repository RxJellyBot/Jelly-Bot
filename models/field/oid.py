import struct
from datetime import datetime
from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from ._base import BaseField
from .exceptions import FieldOidStringInvalid, FieldOidDatetimeOutOfRange, FieldValueInvalid

OID_KEY = "_id"


class ObjectIDField(BaseField):
    def __init__(self, key=None, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``
        - ``readonly`` - ``True``

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False
        if "readonly" not in kwargs:
            kwargs["readonly"] = True

        super().__init__(key or OID_KEY, **kwargs)

    def _check_value_valid_not_none_(self, value):
        if self.allow_none and value is None:
            return

        if isinstance(value, str) and not ObjectId.is_valid(value):
            raise FieldOidStringInvalid(self.key, value)
        if isinstance(value, datetime):
            try:
                ObjectId.from_datetime(value)
            except struct.error:
                raise FieldOidDatetimeOutOfRange(self.key, value)

    def _cast_to_desired_type_(self, value) -> Any:
        if isinstance(value, datetime):
            return ObjectId.from_datetime(value)
        elif isinstance(value, str):
            return ObjectId(value)
        elif isinstance(value, ObjectId):
            return value
        else:
            raise FieldValueInvalid(self.key, value)

    @classmethod
    def none_obj(cls):
        return ObjectId("000000000000000000000000")

    @property
    def expected_types(self):
        return ObjectId, str, datetime

    @property
    def replace_uid_implemented(self) -> bool:
        return True

    def replace_uid(self, collection_inst: Collection, old: ObjectId, new: ObjectId) -> bool:
        return collection_inst.update_many({self.key: old}, {"$set": {self.key: new}}).acknowledged

    def json_schema_property(self, allow_additional=True) -> dict:
        return {
            "bsonType": "objectId"
        }
