from bson import ObjectId
from pymongo.collection import Collection

from ._base import BaseField, FieldInstance
from .exceptions import FieldReadOnly, FieldTypeMismatch, MaxLengthReachedError


class ArrayField(BaseField):
    def __init__(self, key, elem_type: type, default=None, allow_none=False, max_len=0,
                 readonly=False, auto_cast=True, allow_empty=True, stores_uid=False, inst_cls=None):
        if not inst_cls:
            inst_cls = ArrayFieldInstance

        self._elem_type = elem_type
        self._max_len = max_len
        self._allow_empty = allow_empty
        super().__init__(key, default, allow_none=allow_none, readonly=readonly,
                         auto_cast=auto_cast, inst_cls=inst_cls, stores_uid=stores_uid)

    def is_value_valid(self, value) -> bool:
        for v in value:
            if not isinstance(v, self._elem_type):
                return False

        if not self._allow_empty and len(value) == 0:
            return False

        return self.is_type_matched(value)

    @classmethod
    def none_obj(cls):
        return []

    @property
    def expected_types(self):
        return list, tuple, set

    @property
    def replace_uid_implemented(self) -> bool:
        return True

    def replace_uid(self, collection_inst: Collection, old: ObjectId, new: ObjectId) -> bool:
        ack_push = collection_inst.update_many({self.key: {"$in": [old]}}, {"$push": {self.key: new}}).acknowledged
        ack_pull = collection_inst.update_many({self.key: {"$in": [old]}}, {"$pull": {self.key: old}}).acknowledged
        return ack_pull and ack_push


class ModelArrayField(ArrayField):
    def __init__(self, key, model_type, default=None, allow_none=False, max_len=0,
                 readonly=False, auto_cast=True, allow_empty=True, stores_uid=False):
        super().__init__(key, model_type, default, allow_none, max_len, readonly, auto_cast, allow_empty, stores_uid,
                         inst_cls=ModelArrayFieldInstanceFactory.generate(model_type))
        self._model_type = model_type

    def is_value_valid(self, value) -> bool:
        for v in value:
            if not isinstance(v, self._elem_type):
                try:
                    self._model_type.cast_model(v)
                except Exception:
                    return False

        if not self._allow_empty and len(value) == 0:
            return False

        return self.is_type_matched(value)


class ArrayFieldInstance(FieldInstance):
    def add_item(self, item):
        if self.base.read_only:
            raise FieldReadOnly(self.__class__.__qualname__)

        if not isinstance(item, self.base.elem_type):
            raise FieldTypeMismatch(type(item), type(self.base.expected_types), self.base.key)

        if self.value is not None:
            if 0 < self.base.max_len < len(self.value):
                raise MaxLengthReachedError(self.base.max_len)
            else:
                self.value.append(item)
        else:
            self.value = [item]


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
