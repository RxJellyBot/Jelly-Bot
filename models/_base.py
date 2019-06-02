import abc
from bson import ObjectId

from .exceptions import InvalidModelError
from .field import OID_KEY, ObjectIDField


class Model:
    def __init__(self, from_dict=False, **kwargs):
        self._init_fields_(**kwargs)

        if from_dict:
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
        pass

    def serialize(self) -> dict:
        self.pre_serialize()
        return {v.key: v.value for v in self.__dict__.values() if v.value}

    @classmethod
    def parse(cls, dict_):
        return cls(from_dict=True, **dict_)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.serialize()}"
