import abc

from bson import ObjectId
from django.http import QueryDict

from JellyBotAPI.api.static import result


class BaseApiResponse(abc.ABC):
    @abc.abstractmethod
    def __init__(self, param_dict: QueryDict, sender_oid: ObjectId):
        self.__param_dict = param_dict

        self._param_dict = {}

        self._sender_oid = sender_oid

        self._err = dict()
        self._data = dict()
        self._flag = dict()
        self._info = list()
        self._result = None

    def is_success(self) -> bool:
        return len(self._err) == 0 and self.extra_success_conditions()

    @abc.abstractmethod
    def extra_success_conditions(self) -> bool:
        raise NotImplementedError()

    # noinspection PyMethodMayBeStatic
    def _serialize_(self) -> dict:
        return dict()

    @abc.abstractmethod
    def pre_process(self):
        pass

    @abc.abstractmethod
    def process_ifnoerror(self):
        pass

    def to_dict(self) -> dict:
        self.pre_process()
        if len(self._err) == 0:
            self.process_ifnoerror()

        d = self._serialize_()
        d.update(**self.serialize_success())
        d.update(**self.serialize_failed())
        d.update(**self.serialize_extra())
        d[result.SUCCESS] = self.is_success()
        return d

    @abc.abstractmethod
    def serialize_success(self) -> dict:
        return dict()

    @abc.abstractmethod
    def serialize_failed(self) -> dict:
        return dict()

    # noinspection PyMethodMayBeStatic
    def serialize_extra(self) -> dict:
        return dict()

    @property
    def param_dict(self) -> dict:
        return self.__param_dict
