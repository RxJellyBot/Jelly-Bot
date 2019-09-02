from ._base import BaseField, FieldInstance
from .exceptions import FieldReadOnly, FieldTypeMismatch, MaxLengthReachedError


class ArrayField(BaseField):
    def __init__(self, key, elem_type: type, default=None, allow_none=False, max_len=0,
                 readonly=False, auto_cast=True, allow_empty=True):
        self._elem_type = elem_type
        self._max_len = max_len
        self._allow_empty = allow_empty
        super().__init__(key, default, allow_none=allow_none, readonly=readonly,
                         auto_cast=auto_cast, inst_cls=ArrayFieldInstance)

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


class ArrayFieldInstance(FieldInstance):
    def add_item(self, item):
        if self.base.read_only:
            raise FieldReadOnly(self.__class__.__name__)

        if not isinstance(item, self.base.elem_type):
            raise FieldTypeMismatch(type(item), type(self.base.expected_types), self.base.key)

        if self.value is not None:
            if 0 < self.base.max_len < len(self.value):
                raise MaxLengthReachedError(self.base.max_len)
            else:
                self.value.append(item)
        else:
            self.value = [item]
