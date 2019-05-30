import abc
from collections.abc import Iterable
from typing import Tuple

from models.field.exceptions import FieldReadOnly, FieldTypeMismatch, FieldValueInvalid


class BaseField:
    __metaclass__ = abc.ABCMeta

    def __init__(self, key, value=None, allow_none=True, readonly=False):
        self._allow_none = allow_none
        self._readonly = readonly
        self._key = key
        if value is None and not allow_none:
            self._value = self.none_obj()
        else:
            self._value = value

    @property
    @abc.abstractmethod
    def expected_types(self) -> Tuple[type]:
        raise NotImplementedError()

    @property
    def desired_type(self) -> type:
        return self.expected_types[0] if isinstance(self.expected_types, Iterable) else self.expected_types

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._readonly:
            raise FieldReadOnly(self.__class__.__name__)

        self.set_value(value)

    def set_value(self, value):
        if not self.is_type_matched(value):
            raise FieldTypeMismatch(type(value), self.expected_types)

        if not self.is_value_valid(value):
            raise FieldValueInvalid(value)

        if not isinstance(value, (self.desired_type, type(None))):
            value = self.cast_to_desired_type(value)

        self._value = value

    @property
    def allow_none(self):
        return self._allow_none

    @classmethod
    def none_obj(cls):
        raise ValueError(f"Implement none_obj property for {cls}.")

    def is_none(self) -> bool:
        if self._allow_none:
            return self._value is None
        else:
            return self._value == self.none_obj()

    def is_type_matched(self, value) -> bool:
        return isinstance(value, self.expected_types) or (self._allow_none and value is None)

    @abc.abstractmethod
    def is_value_valid(self, value) -> bool:
        raise NotImplementedError()

    def cast_to_desired_type(self, value):
        return self.desired_type(value)

    def __repr__(self):
        return f"{self.__class__.__name__} {'(Read-only) ' if self._readonly else ''}<{self._key}: {self._value}>"
