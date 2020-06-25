import abc
from collections import MutableMapping
from typing import Optional, Set, List

from bson import ObjectId
from pymongo.client_session import ClientSession

from flags import ModelValidityCheckResult
from extutils.checker import arg_type_ensure
from models import OID_KEY
from extutils.utils import to_snake_case, to_camel_case

from .exceptions import (
    InvalidModelError, RequiredKeyNotFilledError, IdUnsupportedError, FieldKeyNotExistError,
    JsonKeyNotExistedError, ModelUncastableError, JsonKeyDuplicatedError, DeleteNotAllowedError, InvalidModelFieldError
)
from .field import ObjectIDField, ModelField, ModelDefaultValueExt, BaseField, IntegerField, ModelArrayField
from .field.exceptions import FieldError
from .warn import warn_keys_not_used, warn_field_key_not_found_for_json_key, warn_action_failed_json_key


class Model(MutableMapping, abc.ABC):
    """
    Should not be inherited from another inherited :class:`Model`.

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
            kwargs = self._json_to_field_kwargs(**kwargs)
        else:
            kwargs = self._camelcase_kwargs(**kwargs)

        try:
            self._input_kwargs(**kwargs)
        except FieldError as e:
            raise InvalidModelFieldError(self.__class__.__qualname__, e)

        not_handled = self._fill_default_vals(
            self.model_field_keys() - {to_camel_case(k) for k in self._dict_})

        if len(not_handled) > 0:
            raise RequiredKeyNotFilledError(self.__class__, not_handled)

        self._init_cache_json_keys()  # Call this to check if there's any duplicated json key
        self._check_validity()

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
            fd = self._inner_dict_get(fk)

            if fd.base.key == jk:
                self._inner_dict_update(fk, v)
                return

            warn_field_key_not_found_for_json_key(self.__class__.__qualname__, jk, "GET")
        else:
            raise JsonKeyNotExistedError(jk, self.__class__.__qualname__)

    def __setattr__(self, fk_sc, value):
        if to_camel_case(fk_sc) in self.model_field_keys():
            self._inner_dict_update(fk_sc, value)
            self._check_validity()
        else:
            if fk_sc.lower() == "id" and not self.WITH_OID:
                raise IdUnsupportedError(self.__class__.__qualname__)
            else:
                raise FieldKeyNotExistError(fk_sc, self.__class__.__qualname__)

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
            fd = self._inner_dict_get(fk)

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
        if not self.WITH_OID and fk_sc == "id":
            raise IdUnsupportedError(self.__class__.__qualname__)

        try:
            fi = self._inner_dict_get(fk_sc)

            if fi:
                return fi.value
        except KeyError:
            pass

        raise FieldKeyNotExistError(fk_sc, self.__class__.__qualname__)

    def __delitem__(self, k) -> None:
        raise DeleteNotAllowedError(self.__class__.__qualname__)

    def __len__(self) -> int:
        return len(self._dict_)

    def __iter__(self):
        self.pre_iter()
        self._check_validity()
        for v in self._dict_.values():
            yield v.base.key

    def __eq__(self, other):
        if isinstance(other, Model):
            return self.to_json() == other.to_json() and type(self) == type(other)
        elif isinstance(other, MutableMapping):
            return self.to_json() == other
        else:
            return False

    def __hash__(self):
        d = self.to_json()

        hash_list = []

        for k, v in d.items():
            if isinstance(v, list):
                v = tuple(v)
            elif isinstance(v, dict):
                v = tuple(v.items())
            elif isinstance(v, Model):
                v = hash(v)

            hash_list.append((k, v))

        return hash(tuple(hash_list))

    def _input_kwargs(self, **kwargs):
        for fk, v in kwargs.items():
            if fk in self.model_field_keys():
                self._inner_dict_create(fk, v)
            else:
                raise FieldKeyNotExistError(fk, self.__class__.__qualname__)

    def _fill_default_vals(self, not_filled):
        filled = set()

        for k in not_filled:
            if k in self.model_field_keys():
                if k not in self.SKIP_DEFAULT_FILLING:
                    default_val = getattr(self, k).default_value
                    if default_val != ModelDefaultValueExt.Required:
                        if default_val != ModelDefaultValueExt.Optional:
                            self._inner_dict_create(k, default_val)

                        filled.add(k)
            else:
                raise FieldKeyNotExistError(k, self.__class__.__qualname__)

        return not_filled - filled - self.SKIP_DEFAULT_FILLING

    def _check_validity(self):
        """
        Check the validity of this :class:`Model` by executing `perform_validity_check()`.

        If the validation failed, execute `on_invalid()`.
        """
        result = self.perform_validity_check()

        if not result.is_success:
            self.on_invalid(result)

    def _inner_dict_create(self, fk, v):
        if fk.lower() == "id" and self.WITH_OID:
            self._dict_["id"] = self.Id.new(v)
        else:
            attr = getattr(self, to_camel_case(fk))

            if attr:
                self._dict_[to_snake_case(fk)] = attr.new(v)
            else:
                raise FieldKeyNotExistError(fk, self.__class__.__qualname__)

    def _inner_dict_get(self, fk):
        if fk.lower() == "id":
            return self._dict_.get("id")
        else:
            return self._dict_[to_snake_case(fk)]

    def _inner_dict_update(self, fk, v):
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
            self._inner_dict_create(fk, v)

    @classmethod
    def _init_cache_to_field(cls):
        d = {v.key: fk for fk, v in cls.__dict__.items() if cls._valid_model_key(fk)}
        if cls.WITH_OID:
            d[OID_KEY] = "Id"

        cls._CacheToField = {cls.__qualname__: d}

    @classmethod
    def _init_cache_field_keys(cls):
        s = {k for k, v in cls.__dict__.items() if cls._valid_model_key(k)}
        if cls.WITH_OID:
            s.add("Id")

        cls._CacheFieldKeys = {cls.__qualname__: s}

    @classmethod
    def _init_cache_json_keys(cls):
        s = set()
        for fk, v in cls.__dict__.items():
            if not cls._valid_model_key(fk):
                continue

            jk = v.key
            if jk in s:
                raise JsonKeyDuplicatedError(jk, cls.__qualname__)

            s.add(jk)

        if cls.WITH_OID:
            s.add(cls.Id.key)

        cls._CacheJsonKeys = {cls.__qualname__: s}

    @classmethod
    def _init_cache_fields(cls):
        s = {v for fk, v in cls.__dict__.items() if cls._valid_model_key(fk)}
        if cls.WITH_OID:
            s.add(cls.Id)

        cls._CacheField = {cls.__qualname__: s}

    @classmethod
    def _valid_model_key(cls, fk: str):
        if fk.lower() == "Id":
            return cls.WITH_OID
        else:
            # Check if the attribute starts with a capitalized letter
            if not fk[0].isupper():
                return False

            # Check if the name of the attribute is all caps, excluding single letter attribute
            # ALL CAPS: class constant, for example: ``WITH_OID``
            # Single letter: X, Y...etc.
            if fk.isupper() and len(fk) > 1:
                return False

            return fk in cls.__dict__ and isinstance(cls.__dict__[fk], BaseField)

    @classmethod
    def _json_to_field_kwargs(cls, **kwargs):
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
    def _camelcase_kwargs(**kwargs):
        tmp = {}

        for k, v in kwargs.items():
            ck = to_camel_case(k)
            tmp[k if k == ck else ck] = v

        return tmp

    def pre_iter(self):
        pass

    def perform_validity_check(self) -> ModelValidityCheckResult:
        """
        Can be overrided to check the validity of the content.

        Need **NOT** to be expensive.
        """
        return ModelValidityCheckResult.default()

    def on_invalid(self, reason=ModelValidityCheckResult.X_UNCATEGORIZED):
        raise InvalidModelError(self.__class__.__qualname__, reason)

    def is_field_none(self, fn, *, raise_on_not_exists=True):
        """
        Check if the field is none/empty.

        :param fn: field name to check (*NOT* key)
        :param raise_on_not_exists: raise `FieldKeyNotExistedError` if the field does not exist
        :raises FieldKeyNotExistedError: if the field does not exist and `raise_on_not_exists` is `True`
        :return: if the field is none/empty
        """
        try:
            return self._inner_dict_get(fn).is_empty()
        except KeyError:
            if raise_on_not_exists:
                raise FieldKeyNotExistError(fn, self.__class__.__qualname__)
            else:
                return True

    @arg_type_ensure
    def set_oid(self, oid: ObjectId):
        self._inner_dict_update("Id", oid)

    def get_oid(self) -> Optional[ObjectId]:
        fi = self._inner_dict_get("Id")

        if fi:
            return fi.value
        else:
            return None

    def clear_oid(self):
        if "id" in self._dict_:
            del self._dict_["id"]

    def to_json(self):
        d = {}

        for v in self._dict_.values():
            if v.value is None:
                d[v.base.key] = None
            elif isinstance(v.base, ModelField):
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
            cls._init_cache_fields()

        return cls._CacheField[cls.__qualname__]

    @classmethod
    def model_field_keys(cls) -> Set[str]:
        """Get the set of all available field keys."""
        if not hasattr(cls, "_CacheFieldKeys") or cls.__qualname__ not in cls._CacheFieldKeys:
            cls._init_cache_field_keys()

        return cls._CacheFieldKeys[cls.__qualname__]

    @classmethod
    def model_json_keys(cls) -> Set[str]:
        """Get the set of all available json keys."""
        if not hasattr(cls, "_CacheJsonKeys") or cls.__qualname__ not in cls._CacheJsonKeys:
            cls._init_cache_json_keys()

        return cls._CacheJsonKeys[cls.__qualname__]

    @classmethod
    def json_key_to_field(cls, json_key) -> Optional[str]:
        """Get the corresponding field key using the provided json key. Return ``None`` if not found."""
        if not hasattr(cls, "_CacheToField") or cls.__qualname__ not in cls._CacheToField:
            cls._init_cache_to_field()

        return cls._CacheToField[cls.__qualname__].get(json_key)

    @classmethod
    def field_to_json_key(cls, field_key) -> Optional[str]:
        """Get the corresponding json key using the provided field key. Return ``None`` if not found."""
        if not hasattr(cls, "_CacheToField") or cls.__qualname__ not in cls._CacheToField:
            cls._init_cache_to_field()

        d = cls._CacheToField[cls.__qualname__]
        for jk, fk in d.items():
            if fk == field_key:
                return jk

        return None

    @classmethod
    def get_field_class_instance(cls, field_key) -> Optional[BaseField]:
        return getattr(cls, field_key, None)

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

        if obj is None:
            return None

        if not isinstance(obj, MutableMapping):
            raise ModelUncastableError(cls.__qualname__, f"Value to be casted is not a `MutableMapping`. > {obj}")

        if isinstance(obj, cls):
            return obj

        init_dict = dict(obj)
        for k in obj:
            if k not in cls.model_json_keys():
                del init_dict[k]

        return cls(**init_dict, from_db=True)

    @classmethod
    def replace_uid(cls, col, old: ObjectId, new: ObjectId, session: ClientSession) -> List[str]:
        """
        Replace the values of the fields which are marked storing the uids.

        :param col: collection instance
        :param old: old value to be replaced
        :param new: new value to replace
        :param session: MongoDB client session

        :return: name of the fields that was failed to complete the replacement if any
        """
        failed_names = []

        for k in cls.model_field_keys():
            fd: BaseField = getattr(cls, k, None)
            if fd and fd.stores_uid:
                result = fd.replace_uid(col, old, new, session)
                if not result:
                    failed_names.append(fd.__class__.__qualname__)

        return failed_names

    def __repr__(self):
        return f"<{self.__class__.__qualname__}: {self._dict_}>"
