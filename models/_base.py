import abc
from collections import MutableMapping
from typing import Optional, Set

from bson import ObjectId

from flags import ModelValidityCheckResult
from extutils.checker import arg_type_ensure
from models import OID_KEY
from extutils.utils import to_snake_case, to_camel_case

from .exceptions import (
    InvalidModelError, RequiredKeyUnfilledError, IdUnsupportedError, FieldKeyNotExistedError,
    JsonKeyNotExistedError, ModelUncastableError
)
from .field import ObjectIDField, ModelField, ModelDefaultValueExt, BaseField, IntegerField, ModelArrayField
from .warn import warn_keys_not_used, warn_field_key_not_found_for_json_key, warn_action_failed_json_key


class Model(MutableMapping, abc.ABC):
    """
    Note:
        self._dict_ = {snake_case_field_key: field_instance, snake_case_field_key: field_instance...}
    """
    SKIP_DEFAULT_FILLING = {"Id"}

    WITH_OID = True

    Id = ObjectIDField()

    def __init__(self, *, from_db=False, **kwargs):
        """
        Field Keys

        >>> Model(FieldKey1="Thing", FieldKey2="Thing"...)

        Json keys:

        >>> Model(json_key1="Thing", json_key2="Thing"...)

        :param from_db: If the data of `kwargs` comes from the database
        :param kwargs: keyword arguments to initialize
        """
        # Doing so to bypass `__setattr__()` which is left for setting the data
        self.__dict__["_dict_"] = {}  # Dict that actually holding the data

        if from_db:
            kwargs = self._json_to_field_kwargs_(**kwargs)
        else:
            kwargs = self._camelcase_kwargs_(**kwargs)

        self._input_kwargs_(**kwargs)

        not_handled = self._fill_default_vals_(
            self.model_field_keys() - {to_camel_case(k) for k in self._dict_.keys()})

        if len(not_handled) > 0:
            raise RequiredKeyUnfilledError(self.__class__, not_handled)

        self._check_validity_()

        unused_keys = kwargs.keys() - self.model_field_keys() - self.SKIP_DEFAULT_FILLING
        if len(unused_keys) > 0:
            warn_keys_not_used(self.__class__.__qualname__, unused_keys)

    def __setitem__(self, jk, v) -> None:
        if jk == OID_KEY:
            if self.WITH_OID:
                self.set_oid(v)
            else:
                raise IdUnsupportedError(self.__class__.__qualname__)

        if jk in self.model_json_keys():
            fk = self.json_key_to_field(jk)
            fd = self._inner_dict_get_(fk)

            if fd.base.key == jk:
                self._inner_dict_update_(fk, v)
                return

            warn_field_key_not_found_for_json_key(self.__class__.__qualname__, jk, "GET")
        else:
            raise JsonKeyNotExistedError(jk, self.__class__.__qualname__)

    def __setattr__(self, fk_sc, value):
        if to_camel_case(fk_sc) in self.model_field_keys():
            self._inner_dict_update_(fk_sc, value)
        else:
            if fk_sc.lower() == "id" and not self.WITH_OID:
                raise IdUnsupportedError(self.__class__.__qualname__)
            else:
                raise FieldKeyNotExistedError(fk_sc, self.__class__.__qualname__)

    def __getitem__(self, jk):
        """
        >>> class DummyModel(Model):
        ...     Int = IntegerField("i")
        >>> m = DummyModel(Int=5)
        >>> self["i"]
        5
        """
        # Must throw `KeyError` for `_id` if `_id` not defined. `pymongo` will check this to determine if
        # it needs to insert `_id`.
        if jk == OID_KEY:
            if self.WITH_OID:
                oid = self.get_oid()
                if oid:
                    return oid
                else:
                    raise KeyError(f"OID of {self.__class__.__qualname__}")
            else:
                raise IdUnsupportedError(self.__class__.__qualname__)

        if jk in self.model_json_keys():
            fk = self.json_key_to_field(jk)
            fd = self._inner_dict_get_(fk)

            if fd.base.key == jk:
                return fd.value

            warn_field_key_not_found_for_json_key(self.__class__.__qualname__, jk, "GET")
        else:
            # The key may be field_key (For Django template)
            fk = self.json_key_to_field(jk)

            if not fk:
                raise JsonKeyNotExistedError(jk, self.__class__.__qualname__)

            try:
                return self.__getattr__(to_snake_case(fk))
            except AttributeError:
                warn_action_failed_json_key(self.__class__.__qualname__, jk, "GET")

        return None

    def __getattr__(self, fk_sc):
        """
        >>> class DummyModel(Model):
        ...     Int = IntegerField("i")
        >>> m = DummyModel(Int=5)
        >>> getattr(m, "int")
        IntegerField<i>
        """
        try:
            fi = self._inner_dict_get_(fk_sc)

            if fi:
                return fi.value
        except KeyError:
            pass

        raise FieldKeyNotExistedError(fk_sc, self.__class__.__qualname__)

    def __delitem__(self, v) -> None:
        delattr(self._dict_, v)

    def __len__(self) -> int:
        return len(self._dict_)

    def __iter__(self):
        self.pre_iter()
        self._check_validity_()
        for v in self._dict_.values():
            yield v.base.key

    def __eq__(self, other):
        if isinstance(other, Model):
            return self.data_dict == other.data_dict and type(self) == type(other)
        else:
            return False

    def __hash__(self):
        return super().__hash__()

    def _input_kwargs_(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.model_field_keys():
                self._inner_dict_create_(k, v)
            else:
                raise FieldKeyNotExistedError(k, self.__class__.__qualname__)

    def _fill_default_vals_(self, not_filled):
        filled = set()

        for k in not_filled:
            if k in self.model_field_keys():
                if k not in self.SKIP_DEFAULT_FILLING:
                    default_val = getattr(self, k).default_value
                    if default_val != ModelDefaultValueExt.Required:
                        if default_val != ModelDefaultValueExt.Optional:
                            self._inner_dict_create_(k, default_val)

                        filled.add(k)
            else:
                raise FieldKeyNotExistedError(k, self.__class__.__qualname__)

        return not_filled - filled - self.SKIP_DEFAULT_FILLING

    def _check_validity_(self):
        result = self.perform_validity_check()

        if not result.is_success:
            self.on_invalid(result)

    def _inner_dict_create_(self, fk, v):
        if fk.lower() == "id" and self.WITH_OID:
            self._dict_["id"] = self.Id.new(v)
        else:
            attr = getattr(self, to_camel_case(fk))

            if attr:
                self._dict_[to_snake_case(fk)] = attr.new(v)
            else:
                raise FieldKeyNotExistedError(fk, self.__class__.__qualname__)

    def _inner_dict_get_(self, fk):
        if fk.lower() == "id":
            return self._dict_.get("id")
        else:
            return self._dict_[to_snake_case(fk)]

    def _inner_dict_update_(self, fk, v):
        if fk.lower() == "id":
            if self.WITH_OID:
                if not isinstance(v, ObjectId):
                    v = ObjectId(v)

                if "id" in self._dict_:
                    self._dict_["id"].force_set(v)
                else:
                    self._dict_["id"] = self.Id.new(v)
            else:
                raise IdUnsupportedError(self.__class__.__qualname__)
        elif to_snake_case(fk) in self._dict_:
            self._dict_[to_snake_case(fk)].value = v
        else:
            self._inner_dict_create_(fk, v)

    @classmethod
    def _init_cache_to_field_(cls):
        d = {v.key: fk for fk, v in cls.__dict__.items() if cls._valid_model_key_(fk)}
        if cls.WITH_OID:
            d[OID_KEY] = "Id"

        cls._CacheToField = {cls.__qualname__: d}

    @classmethod
    def _init_cache_field_keys_(cls):
        s = {k for k, v in cls.__dict__.items() if cls._valid_model_key_(k)}
        if cls.WITH_OID:
            s.add("Id")

        cls._CacheFieldKeys = {cls.__qualname__: s}

    @classmethod
    def _init_cache_json_keys_(cls):
        s = {v.key for fk, v in cls.__dict__.items() if cls._valid_model_key_(fk)}
        if cls.WITH_OID:
            s.add(cls.Id.key)

        cls._CacheJsonKeys = {cls.__qualname__: s}

    @classmethod
    def _init_cache_fields_(cls):
        s = {fk: v for fk, v in cls.__dict__.items() if cls._valid_model_key_(fk)}
        if cls.WITH_OID:
            s["Id"] = cls.Id

        cls._CacheField = {cls.__qualname__: s}

    @classmethod
    def _valid_model_key_(cls, fk):
        if fk.lower() == "Id":
            return cls.WITH_OID
        else:
            return fk[0].isupper() and not fk.isupper() \
                   and fk in cls.__dict__ \
                   and isinstance(cls.__dict__[fk], BaseField)

    @classmethod
    def _json_to_field_kwargs_(cls, **kwargs):
        tmp = {}

        for jk, v in kwargs.items():
            fk = cls.json_key_to_field(jk)  # Filter unrelated json keys
            if fk:
                tmp[fk] = v
            else:
                if jk.lower() == "_id":
                    raise IdUnsupportedError(cls.__qualname__)
                else:
                    raise JsonKeyNotExistedError(jk, cls.__qualname__)

        return tmp

    @staticmethod
    def _camelcase_kwargs_(**kwargs):
        tmp = {}

        for k, v in kwargs.items():
            ck = to_camel_case(k)
            tmp[k if k == ck else ck] = v

        return tmp

    @property
    def data_dict(self):
        return self._dict_

    def pre_iter(self):
        pass

    def perform_validity_check(self) -> ModelValidityCheckResult:
        """Can be overrided to check the validity of the content."""
        return ModelValidityCheckResult.default()

    def on_invalid(self, reason=ModelValidityCheckResult.X_UNCATEGORIZED):
        raise InvalidModelError(self.__class__.__qualname__, reason)

    def is_field_none(self, fk, raise_on_not_exists=True):
        try:
            return self._inner_dict_get_(fk).is_empty()
        except KeyError:
            if raise_on_not_exists:
                raise FieldKeyNotExistedError(fk, self.__class__.__qualname__)
            else:
                return True

    @arg_type_ensure
    def set_oid(self, oid: ObjectId):
        self._inner_dict_update_("Id", oid)

    def get_oid(self) -> Optional[ObjectId]:
        fi = self._inner_dict_get_("Id")

        if fi:
            return fi.value
        else:
            return None

    def clear_oid(self):
        if "Id" in self._dict_:
            del self._dict_["Id"]

    def to_json(self):
        d = {}

        for v in self._dict_.values():
            if isinstance(v.base, ModelField):
                d[v.base.key] = v.value.to_json()
            elif isinstance(v.base, ModelArrayField):
                d[v.base.key] = [mdl.to_json() for mdl in v.value]
            else:
                d[v.base.key] = v.value

        return d

    @classmethod
    def model_fields(cls) -> Set[BaseField]:
        """Get the set of all available fields."""
        if not hasattr(cls, "_CacheField") or cls.__qualname__ not in cls._CacheField:
            cls._init_cache_fields_()

        return cls._CacheField[cls.__qualname__]

    @classmethod
    def model_field_keys(cls) -> Set[str]:
        """Get the set of all available field keys."""
        if not hasattr(cls, "_CacheFieldKeys") or cls.__qualname__ not in cls._CacheFieldKeys:
            cls._init_cache_field_keys_()

        return cls._CacheFieldKeys[cls.__qualname__]

    @classmethod
    def model_json_keys(cls) -> Set[str]:
        """Get the set of all available json keys."""
        if not hasattr(cls, "_CacheJsonKeys") or cls.__qualname__ not in cls._CacheJsonKeys:
            cls._init_cache_json_keys_()

        return cls._CacheJsonKeys[cls.__qualname__]

    @classmethod
    def json_key_to_field(cls, json_key) -> Optional[str]:
        """Get the corresponding field key using the provided json key. Return ``None`` if not found."""
        if not hasattr(cls, "_CacheToField") or cls.__qualname__ not in cls._CacheToField:
            cls._init_cache_to_field_()

        return cls._CacheToField[cls.__qualname__].get(json_key)

    @classmethod
    def field_to_json_key(cls, field_key) -> Optional[str]:
        """Get the corresponding json key using the provided field key. Return ``None`` if not found."""
        if not hasattr(cls, "_CacheToField") or cls.__qualname__ not in cls._CacheToField:
            cls._init_cache_to_field_()

        d = cls._CacheToField[cls.__qualname__]
        for jk, fk in d.items():
            if fk == field_key:
                return jk

        return None

    @classmethod
    def get_field_class(cls, field_key) -> Optional[BaseField]:
        return getattr(cls, field_key)

    @classmethod
    def generate_default(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def cast_model(cls, obj):
        """
        Cast ``obj`` which key is json key to this model class.

        If it matches the conditions below, cast it to this model class.

        - Is not ``None``

            - If it's ``None``, return ``None``.

        - Is not this model class

            - If it's this model class, return ``obj`` without any manipulations.

        - Is a :class:`MutableMapping`

            - If it's not a :class:`MutableMapping`, throw :class:`InvalidModelError`.

        ``obj`` can be a :class:`dict` returned directly from any ``PyMongo`` data acquiring operations.

        The difference between using this and the constructor is that
        the constructor will yield :class:`JsonKeyNotExistedError` if there's additional key in the ``dict``,
        however this will simply omit the additional fields.

        :raises ModelUncastableError: model uncastable
        """
        # TEST: (PASS) cast `None`
        # TEST: (FAIL) cast non-`MutableMapping`
        # TEST: (PASS) cast the model itself
        # TEST: (PASS) `obj` with additional fields

        if obj is None:
            return None

        if not isinstance(obj, MutableMapping):
            raise ModelUncastableError(cls.__qualname__, f"Value to be casted is not a `MutableMapping`. > {obj}")

        if isinstance(obj, cls):
            return obj

        init_dict = dict(obj)
        for k in obj.keys():
            if k not in cls.model_json_keys():
                del init_dict[k]

        return cls(**init_dict, from_db=True)

    def __repr__(self):
        return f"<{self.__class__.__qualname__}: {self.data_dict}>"
