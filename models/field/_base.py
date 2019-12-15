import abc
from collections.abc import Iterable
from typing import Tuple

from bson import ObjectId
from pymongo.collection import Collection

from models.field.exceptions import (
    FieldReadOnly, FieldTypeMismatch, FieldValueInvalid, FieldCastingFailed,
    InvalidFieldInstanceClassError
)


class FieldInstance:
    def __init__(self, base, value=None):
        self._base = base
        self._value = None  # Initialize an empty field

        if value is None and not base.allow_none:
            self.force_set(base.none_obj())
        else:
            self.force_set(value)

    @property
    def base(self):
        return self._base

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.base.read_only:
            raise FieldReadOnly(self.base.__class__.__qualname__)

        self.force_set(value)

    def force_set(self, value):
        if self.base.auto_cast and not isinstance(value, (self.base.desired_type, type(None))):
            try:
                value = self.base.cast_to_desired_type(value)
            except (TypeError, ValueError) as e:
                raise FieldCastingFailed(self.base.key, value, type(value), self.base.desired_type, str(e))

        if not self._base.is_type_matched(value):
            raise FieldTypeMismatch(self.base.key, type(value), self.base.expected_types)

        if not self._base.is_value_valid(value):
            raise FieldValueInvalid(self.base.key, value)

        self._value = value

    def is_none(self) -> bool:
        return self.base.is_none(self.value)

    def __repr__(self):
        return f"Field Instance of {self.base.__class__.__qualname__} " \
               f"{' (Read-only)' if self.base.read_only else ''} " \
               f"<{self.base.key}: {self.value}>"


class BaseField(abc.ABC):
    def __init__(self, key, default=None, allow_none=True, readonly=False, auto_cast=True, inst_cls=FieldInstance,
                 stores_uid=False):
        if not issubclass(inst_cls, FieldInstance):
            raise InvalidFieldInstanceClassError(inst_cls)

        if default is None and not allow_none:
            self._default_value = self.none_obj()
        else:
            self._default_value = default
        self._inst_cls: type(FieldInstance) = inst_cls or FieldInstance
        self._allow_none = allow_none
        self._read_only = readonly
        self._key = key
        self._auto_cast = auto_cast
        self._stores_uid = stores_uid
        if stores_uid and not self.replace_uid_implemented:
            raise RuntimeError(f"replace_uid function not implemented while this field stores user id. "
                               f"Please implement the function. ({self.__class__.__qualname__})")

    @property
    def replace_uid_implemented(self) -> bool:
        return False

    def replace_uid(self, collection_inst: Collection, old: ObjectId, new: ObjectId) -> bool:
        """
        :return: Action has been acknowledges or not.
        """
        raise RuntimeError(f"uid_replace function called but not implemented. ({self.__class__.__qualname__})")

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
    def default_value(self):
        return self._default_value

    @property
    def read_only(self) -> bool:
        return self._read_only

    @property
    def auto_cast(self) -> bool:
        return self._auto_cast

    @property
    def allow_none(self):
        return self._allow_none

    @property
    def instance_class(self) -> type:
        return self._inst_cls

    @property
    def stores_uid(self) -> bool:
        return self._stores_uid

    @classmethod
    def none_obj(cls):
        raise ValueError(f"None object not implemented for {cls}.")

    def is_type_matched(self, value) -> bool:
        return isinstance(value, self.expected_types) or (self._allow_none and value is None)

    @abc.abstractmethod
    def is_value_valid(self, value) -> bool:
        raise NotImplementedError()

    def cast_to_desired_type(self, value):
        return self.desired_type(value)

    def new(self, val=None):
        return self.instance_class(self, val)

    def is_none(self, value) -> bool:
        if self.allow_none:
            return value is None
        else:
            return value == self.none_obj()

    def __repr__(self):
        return f"{self.__class__.__qualname__} {' (Read-only)' if self._read_only else ''} <{self._key}>"
