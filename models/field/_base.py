import abc
from collections.abc import Iterable
from typing import Tuple, Type, Any, final

from bson import ObjectId
from pymongo.collection import Collection

from models.field.exceptions import (
    FieldReadOnlyError, FieldTypeMismatchError, FieldCastingFailedError, FieldNoneNotAllowedError,
    FieldInstanceClassInvalidError, FieldInvalidDefaultValueError, FieldValueRequiredError
)

from ._default import ModelDefaultValueExt


class FieldInstance:
    """Field instance class. This class actually stores the value."""
    NULL_VAL_SENTINEL = object()

    def __init__(self, base: 'BaseField', value=NULL_VAL_SENTINEL):
        """
        :raises FieldValueRequired: If the default value indicates the field requires value but turns out not
        :raises ValueError: Field extended default value unhandled
        """
        self._base = base
        self._value = None  # Initialize an empty class field

        # Skipping type check on init (may fill `None`)
        if value in (None, FieldInstance.NULL_VAL_SENTINEL) and not base.allow_none:
            self.force_set(base.none_obj())
        elif ModelDefaultValueExt.is_default_val_ext(base.default_value) and \
                (ModelDefaultValueExt.is_default_val_ext(value) or value == FieldInstance.NULL_VAL_SENTINEL):
            if base.default_value == ModelDefaultValueExt.Required:
                raise FieldValueRequiredError(self.base.key)
            elif base.default_value == ModelDefaultValueExt.Optional:
                self.force_set(base.none_obj())
            else:
                raise ValueError("Field extended default value unhandled.")
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
        """Set the value with readonly check."""
        if self.base.read_only:
            raise FieldReadOnlyError(self.base.__class__.__qualname__)

        self.force_set(value)

    def force_set(self, value):
        """Setting the value while ignoring the readonly check."""
        self.base.check_value_valid(value, attempt_cast=self.base.auto_cast)

        # Perform cast whenever auto cast is set to `True`.
        if self.base.auto_cast:
            try:
                value = self.base.cast_to_desired_type(value)
            except (TypeError, ValueError) as e:
                raise FieldCastingFailedError(self.base.key, value, self.base.desired_type, exc=e)

        self._value = value

    def is_empty(self) -> bool:
        return self.base.is_empty(self.value)

    def __repr__(self):
        return f"<{self.base.key}{'(ro)' if self.base.read_only else ''}: {self.value}>"

    def __eq__(self, other):
        if isinstance(other, FieldInstance) and type(self) == type(other):
            return self.__dict__ == other.__dict__
        else:
            return False


class BaseField(abc.ABC):
    """
    Field class. This class acts as a template of each field for a :class:`models.Model`.

    Default properties if not specified on construction
        - ``default`` - ``None``
        - ``allow_none`` - ``True`` | Always ``True`` if ``none_obj()`` is ``None``
        - ``readonly`` - ``False``
        - ``auto_cast`` - ``True``
        - ``inst_cls`` - :class:`FieldInstance`
        - ``stores_uid`` - ``False``
    """

    def __init__(self, key: str, *, default: Any = None, allow_none: bool = True, readonly: bool = False,
                 auto_cast: bool = True, inst_cls: Type[FieldInstance] = FieldInstance, stores_uid: bool = False):
        """
        Initialize a field.

        Default values
            - ``default`` - ``None``
            - ``allow_none`` - ``True`` | Always ``True`` if ``none_obj()`` is ``None``
            - ``readonly`` - ``False``
            - ``auto_cast`` - ``True``
            - ``inst_cls`` - :class:`FieldInstance`
            - ``stores_uid`` - ``False``

        :param key: key of the field (will be used in database)
        :param default: default value of the field
        :param allow_none: if the field is allowed to store `None`
        :param readonly: if the field is readonly
        :param auto_cast: if the field will autocast the value to be stored
        :param inst_cls: `FieldInstance` class to be used
        :param stores_uid: if the field will store UID
        """
        # region Setting field properties
        self._allow_none = self.none_obj() is None or allow_none
        self._read_only = readonly
        self._key = key
        self._auto_cast = auto_cast
        # endregion

        # region Setting stores UID
        self._stores_uid = stores_uid
        if stores_uid and not self.replace_uid_implemented:
            raise RuntimeError(f"replace_uid function not implemented while this field stores user id. "
                               f"Please implement the function. ({self.__class__.__qualname__})\n"
                               f"Override the property `replace_uid_implemented` if the function is implemented.")
        # endregion

        # region Setting default value
        if default is not None and not ModelDefaultValueExt.is_default_val_ext(default):
            try:
                self.check_value_valid(default)
            except Exception as e:
                raise FieldInvalidDefaultValueError(self.key, default, exc=e)

        if default is None and not allow_none:
            self._default_value = self.none_obj()
        else:
            self._default_value = default
        # endregion

        # region Setting instance class
        if not issubclass(inst_cls, FieldInstance):
            raise FieldInstanceClassInvalidError(key, inst_cls)
        self._inst_cls: Type[FieldInstance] = inst_cls or FieldInstance
        # endregion

    @property
    def replace_uid_implemented(self) -> bool:
        """The value should be overrided if `replace_uid()` is implemented."""
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
    @final
    def desired_type(self) -> type:
        return self.expected_types[0] if isinstance(self.expected_types, Iterable) else self.expected_types

    @property
    @final
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
    @abc.abstractmethod
    def none_obj(cls) -> Any:
        raise ValueError(f"None object not implemented for {cls}.")

    def _check_type_matched_not_none(self, value, *, attempt_cast=False):
        """Hook of value type checking when the value is not ``None`` and not a extended default value."""
        pass

    def _check_value_valid_not_none(self, value):
        """Hook of value validity checking when the value is not ``None`` and not a extended default value."""
        pass

    def check_type_matched(self, value, *, attempt_cast=False):
        # Check if the value is `None`.
        if not self.allow_none and value is None:
            raise FieldNoneNotAllowedError(self.key)

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
            raise FieldTypeMismatchError(self.key, type(value), value, expected_types)

        if value is not None and not ModelDefaultValueExt.is_default_val_ext(value):
            self._check_type_matched_not_none(value, attempt_cast=attempt_cast or self.auto_cast)

    def is_type_matched(self, value, *, attempt_cast=False) -> bool:
        try:
            self.check_type_matched(value, attempt_cast=attempt_cast)
        except Exception:
            return False
        else:
            return True

    def check_value_valid(self, value, *, attempt_cast=False):
        """
        Check the validity of the value.

        Check the value type first.
        """
        self.check_type_matched(value, attempt_cast=attempt_cast)

        if value is not None and not ModelDefaultValueExt.is_default_val_ext(value):
            self._check_value_valid_not_none(value)

    def is_value_valid(self, value, *, attempt_cast=False) -> bool:
        try:
            self.check_value_valid(value, attempt_cast=attempt_cast)
        except Exception:
            return False
        else:
            return True

    def cast_to_desired_type(self, value) -> Any:
        """
        Cast the value to the desired type.

        Does not perform type cast if the value type is already the desired type.
        """
        if type(value) == self.desired_type:
            return value
        elif value is None:
            if self.allow_none:
                return None
            else:
                raise FieldNoneNotAllowedError(self.key)
        else:
            return self._cast_to_desired_type(value)

    def _cast_to_desired_type(self, value) -> Any:
        """
        Method hook to be called if `cast_to_desired_type()` is called
        and the given value type is not the desired type.
        """
        return self.desired_type(value)

    @final
    def new(self, val=None) -> FieldInstance:
        return self.instance_class(self, val if val is not None else self.default_value)

    @final
    def is_empty(self, value) -> bool:
        """
        Check if the value is an empty value (either is ``None`` or ``none_obj``.
        """
        return value is None or value == self.none_obj()

    def __repr__(self):
        return f"{self.__class__.__qualname__}{' (Read-only)' if self._read_only else ''}<{self._key}>"

    def __eq__(self, other):
        if isinstance(other, BaseField) and type(self) == type(other):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __hash__(self):
        return hash((self.__class__, self.key))
