import math

from bson import ObjectId
from pymongo.collection import Collection

from ._base import BaseField, FieldInstance
from .exceptions import (
    FieldReadOnly, FieldValueTypeMismatch, FieldMaxLengthReached, FieldCastingFailed, FieldEmptyValueNotAllowed
)


class ArrayField(BaseField):
    def __init__(self, key, elem_type: type, *, max_len=0, allow_empty=True, **kwargs):
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

        cast_type = None
        if issubclass(self._elem_type, Model):
            cast_type = self._elem_type

        for v in value:
            value_type = type(v)

            if cast_type:
                cast_type.cast_model(v)
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


class ModelArrayField(ArrayField):
    def __init__(self, key, model_type, **kwargs):
        if "inst_cls" not in kwargs:
            kwargs["inst_cls"] = ModelArrayFieldInstanceFactory.generate(model_type)

        super().__init__(key, model_type, **kwargs)
        self._model_type = model_type


class ArrayFieldInstance(FieldInstance):
    def __init__(self, base, value=None):
        if not isinstance(base, ArrayField):
            raise ValueError(f"`ArrayFieldInstance` can only be used when the base class is {ArrayField}. ({base})")

        super().__init__(base, value)


class ModelArrayFieldInstanceFactory:
    @staticmethod
    def generate(model_type):
        def get_val(self):
            return [model_type.cast_model(v) for v in self._value]

        def set_val(self, value):
            if self.base.read_only:
                raise FieldReadOnly(self.base.__class__.__qualname__)

            self.force_set(value)

        return type(f"{model_type.__name__}ModelArrayInstance",
                    (FieldInstance,),
                    {"value": property(fget=get_val, fset=set_val)},)
