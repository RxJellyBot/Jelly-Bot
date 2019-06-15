import abc
from typing import Tuple

from bson import ObjectId

from .exceptions import InvalidModelError
from .field import OID_KEY, ObjectIDField


class Model:
    default_vals: Tuple

    @classmethod
    def get_default_dict(cls) -> dict:
        if not cls.default_vals:
            raise ValueError(f"Default values not defined in the Model class. ({cls.__name__})")
        return {k: v for k, v in cls.default_vals}

    def __init__(self, from_db=False, incl_oid=True, **kwargs):
        """
        :param from_db: `kwargs` comes from the database.
        :param incl_oid: Include `_id` field when initializing. Omitted when `from_db` is False.
        :param kwargs: Arguments for fields to be initialized.
        """
        self._init_fields_(**kwargs)

        if from_db:
            if incl_oid:
                self.id = ObjectIDField()
            self._json_fill_in_(**kwargs)
        else:
            self._match_fields_(**kwargs)

        if not self.is_valid():
            self.handle_invalid()

    @abc.abstractmethod
    def _init_fields_(self, **kwargs):
        raise NotImplementedError()

    def _match_fields_(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__dict__[k].set_value(kwargs[k])

    def _json_fill_in_(self, **json):
        for k, v in self.__dict__.items():
            json_key = v.key
            if json_key in json:
                self.__dict__[k].set_value(json[json_key])

    def is_valid(self):
        return True

    def handle_invalid(self):
        raise InvalidModelError(self.__class__.__name__, "Not Specified.")

    def set_oid(self, oid: ObjectId):
        self.id = ObjectIDField(OID_KEY, oid)

    def pre_serialize(self):
        """
        Raise `PreserializationFailedError` if the process failed.

        :exception: PreserializationFailedError
        :return: None
        """
        pass

    def serialize(self, include_oid=True) -> dict:
        self.pre_serialize()
        return {v.key: v.value for v in self.__dict__.values()
                if v.value is not None and (include_oid or v.key != OID_KEY)}

    @classmethod
    def parse(cls, dict_):
        return cls(from_db=True, **dict_)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.serialize()}"

    def __getattr__(self, item):
        return None

    @classmethod
    def model_keys(cls) -> dict:
        return {k: v for k, v in cls.__dict__.items() if k[0].isupper() and isinstance(v, str) and v.islower()}


class ModelDefaultValueExtension:
    Required = object()
    Optional = object()
