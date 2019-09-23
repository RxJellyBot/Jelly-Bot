import abc

from bson import ObjectId
from django.http import QueryDict

from JellyBot.api.static import result


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
        return len(self._err) == 0 and self.pass_condition()

    @abc.abstractmethod
    def pass_condition(self) -> bool:
        return True

    # noinspection PyMethodMayBeStatic
    def _serialize_(self) -> dict:
        return dict()

    @abc.abstractmethod
    def pre_process(self):
        pass

    @abc.abstractmethod
    def process_pass(self):
        pass

    def to_dict(self) -> dict:
        self.pre_process()
        if len(self._err) == 0:
            self.process_pass()

        d = self._serialize_()
        is_success = self.is_success()

        if is_success:
            d.update(**self.serialize_success())
        else:
            d.update(**self.serialize_failed())

        d.update(**self.serialize_extra())
        d[result.SUCCESS] = is_success
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
