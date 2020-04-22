import abc
from collections.abc import Iterable
from typing import Tuple

from bson import ObjectId
from pymongo.collection import Collection

from models.field.exceptions import (
    FieldReadOnly, FieldTypeMismatch, FieldCastingFailed, FieldNoneNotAllowed,
    FieldInstanceClassInvalid, FieldInvalidDefaultValue
)

from ._default import ModelDefaultValueExt


class FieldInstance:
    def __init__(self, base, value=None, skip_type_check=True):
        self._base = base
        self._value = None  # Initialize an empty field

        # Skipping type check on init (may fill `None`)
        if value is None and not base.allow_none:
            self.force_set(base.none_obj(), skip_type_check)
        else:
            self.force_set(value, skip_type_check)

    @property
    def base(self):
        return self._base

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """Set the value with readonly check."""
        if self.base.read_only:
            raise FieldReadOnly(self.base.__class__.__qualname__)

        self.force_set(value)

    def force_set(self, value, skip_type_check=False):
        """Setting the value while passing the readonly check."""
        self.base.check_value_valid(value, skip_type_check=skip_type_check, pass_on_castable=self.base.auto_cast)

        # Perform cast whenever auto cast is set to `True`.
        if self.base.auto_cast:
            try:
                value = self.base.cast_to_desired_type(value)
            except (TypeError, ValueError) as e:
                raise FieldCastingFailed(self.base.key, value, self.base.desired_type, exc=e)

        self._value = value

    def is_empty(self) -> bool:
        return self.base.is_empty(self.value)

    def __repr__(self):
        return f"Field Instance of {self.base.__class__.__qualname__} " \
               f"{' (Read-only)' if self.base.read_only else ''} " \
               f"<{self.base.key}: {self.value}>"


class BaseField(abc.ABC):
    def __init__(self, key, default=None, allow_none=True, readonly=False, auto_cast=True, inst_cls=FieldInstance,
                 stores_uid=False):
        if not issubclass(inst_cls, FieldInstance):
            raise FieldInstanceClassInvalid(key, inst_cls)

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

        if default is not None and not ModelDefaultValueExt.is_default_val_ext(default):
            try:
                self.check_value_valid(default)
            except Exception as e:
                raise FieldInvalidDefaultValue(key, default, exc=e)

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

    def _check_type_matched_not_none_(self, value, *, pass_on_castable=False):
        """Hook of value type checking when the value is not `None`."""
        pass

    def _check_value_valid_not_none_(self, value, *, skip_type_check=False, pass_on_castable=False):
        """Hook of value validity checking when the value is not `None`."""
        pass

    def check_type_matched(self, value, *, pass_on_castable=False):
        # Check if the value is `None`.
        if not self.allow_none and value is None:
            raise FieldNoneNotAllowed(self.key)

        # Expected types may not be an iterable
        expected_types = self.expected_types
        if isinstance(expected_types, tuple):
            expected_types = list(expected_types)
        elif isinstance(expected_types, type):
            expected_types = [expected_types]

        if self.allow_none:
            expected_types.append(type(None))

        # Check value type
        if not type(value) in expected_types:
            raise FieldTypeMismatch(self.key, type(value), expected_types)

        if value is not None:
            self._check_type_matched_not_none_(value, pass_on_castable=pass_on_castable or self.auto_cast)

    def is_type_matched(self, value, *, pass_on_castable=False) -> bool:
        try:
            self.check_type_matched(value, pass_on_castable=pass_on_castable)
        except Exception as _:
            return False
        else:
            return True

    def check_value_valid(self, value, *, skip_type_check=False, pass_on_castable=False):
        """
        Check the validity of the value.

        Check the value type first.
        """
        # Check value type
        if not skip_type_check:
            self.check_type_matched(value, pass_on_castable=pass_on_castable)

        if value is not None:
            self._check_value_valid_not_none_(
                value, skip_type_check=skip_type_check, pass_on_castable=pass_on_castable or self.auto_cast)

    def is_value_valid(self, value, *, skip_type_check=False, pass_on_castable=False) -> bool:
        try:
            self.check_value_valid(value, skip_type_check=skip_type_check, pass_on_castable=pass_on_castable)
        except Exception as _:
            return False
        else:
            return True

    def cast_to_desired_type(self, value):
        """
        Cast the value to the desired type.

        Does not perform type cast if the value type is already the desired type.
        """
        if type(value) == self.desired_type:
            return value
        elif self.allow_none and value is None:
            return None
        else:
            return self.desired_type(value)

    def _cast_to_desired_type_(self, value):
        """
        Method hook to be called if `cast_to_desired_type()` is called
        and the given value type is not the desired type.
        """
        return self.desired_type(value)

    def new(self, val=None):
        return self.instance_class(self, val or self.default_value)

    def is_empty(self, value) -> bool:
        """
        Check if the value is an empty value.

        If `None` is allowed, it will check if the value is `None`.
        If `None` is not allowed, it will check if the value is either the none object or is `None`.
        """
        if self.allow_none:
            return value is None
        else:
            return value == self.none_obj() or value is None

    def __repr__(self):
        return f"{self.__class__.__qualname__} {' (Read-only)' if self._read_only else ''} <{self._key}>"
