import abc
from typing import MutableMapping

from bson import ObjectId

from flags import ModelValidityCheckResult
from extutils.checker import param_type_ensure
from models import OID_KEY
from models.field import BaseField
from extutils.utils import to_snake_case, to_camel_case

from .exceptions import *
from .field import ObjectIDField, ModelField
from .warn import warn_keys_not_used, warn_field_key_not_found_for_json_key, warn_action_failed_json_key


class Model(MutableMapping, abc.ABC):
    """
    Note:
        self._dict_ = {snake_case_field_key: field_instance, snake_case_field_key: field_instance...}
    """
    SKIP_DEFAULT_FILLING = {"Id"}

    WITH_OID = True

    Id = ObjectIDField()

    def __init__(self, from_db=False, **kwargs):
        """
        :param from_db: If the data of `kwargs` comes from the database.
        :param kwargs: Example:
                        Field Keys: Model(FieldKey1=Thing, FieldKey2=Thing...)
                        Json Keys: Model(json_key1=Thing, json_key2=Thing...)
        """
        self.__dict__["_dict_"] = {}

        if from_db:
            kwargs = self._json_to_field_kwargs_(**kwargs)
        else:
            kwargs = self._camelcase_kwargs_(**kwargs)

        self._input_kwargs_(**kwargs)

        not_handled = self._fill_default_vals_(self.model_fields() - {to_camel_case(k) for k in self._dict_.keys()})

        if len(not_handled) > 0:
            raise RequiredKeyUnfilledError(not_handled)

        self._check_validity_()

        unused_keys = kwargs.keys() - self.model_fields() - self.SKIP_DEFAULT_FILLING
        if len(unused_keys) > 0:
            warn_keys_not_used(self.__class__.__qualname__, unused_keys)

    def _input_kwargs_(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                self._inner_dict_create_(k, v)

    def _fill_default_vals_(self, not_filled):
        filled = set()

        for k in not_filled:
            if k in self.model_fields():
                if k not in self.SKIP_DEFAULT_FILLING:
                    default_val = getattr(self, k).default_value
                    if default_val != ModelDefaultValueExt.Required:
                        if default_val != ModelDefaultValueExt.Optional:
                            self._inner_dict_create_(k, default_val)

                        filled.add(k)
            else:
                raise KeyNotExistedError(k, self.__class__.__qualname__)

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
                raise KeyNotExistedError(fk, self.__class__.__qualname__)

    def _inner_dict_get_(self, fk):
        if fk.lower() == "id":
            return self._dict_["id"]
        else:
            return self._dict_[to_snake_case(fk)]

    def _inner_dict_update_(self, fk, v):
        if fk.lower() == "id" and self.WITH_OID:
            if not isinstance(v, ObjectId):
                v = ObjectId(v)

            if "id" in self._dict_:
                self._dict_["id"].force_set(v)
            else:
                self._dict_["id"] = self.Id.new(v)
        else:
            self._dict_[to_snake_case(fk)].value = v

    def __setitem__(self, jk, v) -> None:
        if jk in self.model_json():
            try:
                fk = self.json_key_to_field(jk)
                fd = self._inner_dict_get_(fk)

                if fd.base.key == jk:
                    self._inner_dict_update_(fk, v)
                    return
            except KeyError:
                if jk == OID_KEY:
                    self._inner_dict_create_(self.json_key_to_field(jk), v)
            else:
                warn_field_key_not_found_for_json_key(self.__class__.__qualname__, jk, "GET")
        else:
            if jk == OID_KEY:
                if self.WITH_OID:
                    self.set_oid(v)
                else:
                    raise IdUnsupportedError(self.__class__.__qualname__)
            else:
                warn_action_failed_json_key(self.__class__.__qualname__, jk, "SET")

    def __setattr__(self, fk_sc, value):
        if to_camel_case(fk_sc) in self.model_fields():
            self._inner_dict_update_(fk_sc, value)

        raise KeyNotExistedError(fk_sc, self.__class__.__qualname__)

    def __getitem__(self, jk):
        # Must throw `KeyError` for `_id` if `_id` not defined. `pymongo` will check this to determine if
        # it needs to insert `_id`.
        if jk in self.model_json():
            fk = self.json_key_to_field(jk)
            fd = self._inner_dict_get_(fk)

            if fd.base.key == jk:
                return fd.value

            warn_field_key_not_found_for_json_key(self.__class__.__qualname__, jk, "GET")
        else:
            if jk == OID_KEY:
                if self.WITH_OID:
                    return self.get_oid()
                else:
                    raise IdUnsupportedError(self.__class__.__qualname__)
            else:
                # The key may be field_key (For Django template)
                try:
                    return self.__getattr__(to_snake_case(self.json_key_to_field(jk)))
                except AttributeError:
                    warn_action_failed_json_key(self.__class__.__qualname__, jk, "GET")

        return None

    def __getattr__(self, fk_sc):
        try:
            fd = self._inner_dict_get_(fk_sc)

            if fd:
                return fd.value
        except KeyError:
            pass

        raise AttributeError(fk_sc)

    def __delitem__(self, v) -> None:
        delattr(self._dict_, v)

    def __len__(self) -> int:
        return len(self._dict_)

    def __iter__(self):
        self.pre_iter()
        self._check_validity_()
        for v in self._dict_.values():
            yield v.base.key

    def pre_iter(self):
        pass

    def perform_validity_check(self) -> ModelValidityCheckResult:
        return ModelValidityCheckResult.default()

    def on_invalid(self, reason=ModelValidityCheckResult.X_UNCATEGORIZED):
        raise InvalidModelError(self.__class__.__qualname__, reason)

    def is_field_none(self, fk, raise_on_not_exists=True):
        try:
            return self._inner_dict_get_(fk).is_none()
        except KeyError:
            if raise_on_not_exists:
                raise KeyNotExistedError(fk, self.__class__.__qualname__)
            else:
                return True

    @param_type_ensure
    def set_oid(self, oid: ObjectId):
        self._inner_dict_update_("Id", oid)

    def get_oid(self):
        return self._inner_dict_get_("Id").value

    def clear_oid(self):
        if "Id" in self._dict_:
            del self._dict_["Id"]

    def to_json(self):
        d = {}

        for v in self._dict_.values():
            d[v.base.key] = v.value.to_json() if isinstance(v.base, ModelField) else v.value

        return d

    @classmethod
    def model_fields(cls) -> set:
        if not hasattr(cls, "_CacheField") or cls.__qualname__ not in cls._CacheField:
            s = {k for k, v in cls.__dict__.items() if cls._valid_model_key_(k)}
            if cls.WITH_OID:
                s.add("Id")

            cls._CacheField = {cls.__qualname__: s}

        return cls._CacheField[cls.__qualname__]

    @classmethod
    def model_json(cls) -> set:
        if not hasattr(cls, "_CacheJson") or cls.__qualname__ not in cls._CacheJson:
            s = {v.key for fk, v in cls.__dict__.items() if cls._valid_model_key_(fk)}
            if cls.WITH_OID:
                s.add(cls.Id.key)

            cls._CacheJson = {cls.__qualname__: s}

        return cls._CacheJson[cls.__qualname__]

    @classmethod
    def cast_model(cls, obj):
        if obj is not None and cls is not None and not isinstance(obj, cls):
            return cls(**obj, from_db=True)

        return obj

    @classmethod
    def json_key_to_field(cls, json_key) -> str:
        if not hasattr(cls, "_CacheToField") or cls.__qualname__ not in cls._CacheToField:
            d = {v.key: fk for fk, v in cls.__dict__.items() if cls._valid_model_key_(fk)}
            if cls.WITH_OID:
                d[OID_KEY] = "Id"

            cls._CacheToField = {cls.__qualname__: d}

        return cls._CacheToField[cls.__qualname__].get(json_key)

    @classmethod
    def generate_default(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    def _valid_model_key_(cls, fk):
        if fk.lower() == "Id":
            return cls.WITH_OID
        else:
            return fk[0].isupper() and not fk.isupper() and \
                   fk in cls.__dict__ and isinstance(cls.__dict__[fk], BaseField)

    @staticmethod
    def _camelcase_kwargs_(**kwargs):
        tmp = {}

        for k, v in kwargs.items():
            ck = to_camel_case(k)
            tmp[k if k == ck else ck] = v

        return tmp

    @classmethod
    def _json_to_field_kwargs_(cls, **kwargs):
        tmp = {}

        for k, v in kwargs.items():
            fk = cls.json_key_to_field(k)  # Filter unrelated json keys
            if fk:
                tmp[fk] = v

        return tmp

    def __repr__(self):
        return f"<{self.__class__.__qualname__}: {self._dict_}>"


class ModelDefaultValueExtItem:
    def __init__(self, s):
        self._name = s

    def __repr__(self):
        return f"<Default: {self._name}>"


class ModelDefaultValueExt:
    Required = ModelDefaultValueExtItem("Required")
    Optional = ModelDefaultValueExtItem("Optional")
