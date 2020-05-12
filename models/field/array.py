import math
from collections import abc

from bson import ObjectId
from pymongo.collection import Collection

from ._base import BaseField, FieldInstance
from .exceptions import (
    FieldModelClassInvalid, FieldValueTypeMismatch, FieldMaxLengthReached,
    FieldCastingFailed, FieldEmptyValueNotAllowed
)


class ArrayField(BaseField):
    def __init__(self, key, elem_type: type, *, max_len=0, allow_empty=True, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``
        - ``inst_cls`` - :class:`ArrayFieldInstance`

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = ArrayFieldInstance
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        # Check max length
        if max_len < 0:
            raise ValueError("Max length of the array field must > 0.")
        if type(max_len) != int:
            raise TypeError("Max length of the array must be `int`.")

        self._elem_type = elem_type
        self._max_len = max_len
        self._allow_empty = allow_empty
        super().__init__(key, **kwargs)

    def _check_value_valid_not_none_(self, value):
        # Check emptiness
        if not self._allow_empty and len(value) == 0:
            raise FieldEmptyValueNotAllowed(self.key)

        # Check length
        if len(value) > self.max_len:
            raise FieldMaxLengthReached(self.key, len(value), self.max_len)

    def _check_type_matched_not_none_(self, value, *, attempt_cast=False):
        from models import Model

        # If the element type is `Model`, try to cast the element of the field later
        model_type = None
        if issubclass(self._elem_type, Model):
            model_type = self._elem_type

        for v in value:
            value_type = type(v)

            if model_type:
                # If `model_type` is available and `v` is potentially castable, attempt the cast
                # Otherwise, throw `FieldValueTypeMismatch`
                if isinstance(v, abc.MutableMapping):
                    model_type.cast_model(v)
                else:
                    raise FieldValueTypeMismatch(self.key, value_type, (model_type, abc.MutableMapping))
            elif not value_type == self._elem_type:
                if not attempt_cast:
                    raise FieldValueTypeMismatch(self.key, value_type, self.elem_type)

                try:
                    self._elem_type(v)
                except Exception as e:
                    raise FieldCastingFailed(self.key, v, self.elem_type, exc=e)

    @classmethod
    def none_obj(cls):
        return []

    @property
    def expected_types(self):
        return list, tuple, set

    @property
    def elem_type(self):
        return self._elem_type

    @property
    def max_len(self):
        return self._max_len or math.inf

    def cast_to_desired_type(self, value):
        self.check_value_valid(value, attempt_cast=self.auto_cast)

        if self.allow_none and value is None:
            return None

        v_new = []
        for v in value:
            value_type = type(v)

            if not value_type == self.elem_type:
                v = self.elem_type(v)

            v_new.append(v)

        return v_new

    @property
    def replace_uid_implemented(self) -> bool:
        return True

    def replace_uid(self, collection_inst: Collection, old: ObjectId, new: ObjectId) -> bool:
        ack_push = collection_inst.update_many({self.key: {"$in": [old]}}, {"$push": {self.key: new}}).acknowledged
        ack_pull = collection_inst.update_many({self.key: {"$in": [old]}}, {"$pull": {self.key: old}}).acknowledged
        return ack_pull and ack_push

    def json_schema_property(self, allow_additional=True) -> dict:
        return {
            "bsonType": "array"
        }


class ModelArrayField(ArrayField):
    def __init__(self, key, model_type, **kwargs):
        from models import Model

        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = ModelArrayFieldInstanceFactory.generate(model_type)

        if not issubclass(model_type, Model):
            raise FieldModelClassInvalid(key, model_type)

        super().__init__(key, model_type, **kwargs)
        self._model_type = model_type

    def cast_to_desired_type(self, value):
        self.check_value_valid(value, attempt_cast=self.auto_cast)

        if self.allow_none and value is None:
            return None

        v_new = []
        for v in value:
            if not type(v) == self._model_type:
                v = self._model_type.cast_model(v)

            v_new.append(v)

        return v_new

    def json_schema_property(self, allow_additional=True) -> dict:
        return {
            "bsonType": "array",
            "items": self._model_type.generate_json_schema(allow_additional=allow_additional)
        }


class ArrayFieldInstance(FieldInstance):
    def __init__(self, base, value=None):
        if not isinstance(base, ArrayField):
            raise ValueError(f"`ArrayFieldInstance` can only be used when the base class is {ArrayField}. ({base})")

        super().__init__(base, value)


class ModelArrayFieldInstanceFactory:
    @staticmethod
    def generate(model_type):
        return type(f"{model_type.__name__}ModelArrayInstance",
                    (FieldInstance,),
                    {}, )
