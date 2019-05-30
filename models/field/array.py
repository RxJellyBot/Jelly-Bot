from typing import Iterable

from ._base import BaseField
from .exceptions import FieldReadOnly, FieldTypeMismatch, MaxLengthReachedError


class ArrayField(BaseField):
    def __init__(self, key, elem_type: type, arr: Iterable = None, allow_none=False, max_len=5, readonly=False):
        self._elem_type = elem_type
        self._max_len = max_len
        super().__init__(key, arr, allow_none, readonly=readonly)

    def is_value_valid(self, value) -> bool:
        for v in value:
            if not isinstance(v, self._elem_type):
                return False

        return self.is_type_matched(value)

    def add(self, item):
        if self._readonly:
            raise FieldReadOnly(self.__class__.__name__)

        if not isinstance(item, self._elem_type):
            raise FieldTypeMismatch(type(item), type(self.expected_types), self.key)

        if self._value is not None:
            if len(self._value) > self._max_len:
                raise MaxLengthReachedError(self._max_len)
            else:
                self._value.append(item)
        else:
            self._value = [item]

    @classmethod
    def none_obj(cls):
        return []

    @property
    def expected_types(self):
        return list, tuple, set
