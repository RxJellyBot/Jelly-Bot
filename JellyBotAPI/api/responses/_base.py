import abc

from django.http import QueryDict

from JellyBotAPI.api.static import result


class BaseApiResponse:
    @abc.abstractmethod
    def __init__(self, param_dict: QueryDict):
        raise NotImplementedError()

    @abc.abstractmethod
    def is_success(self) -> bool:
        raise NotImplementedError()

    def _serialize_(self) -> dict:
        return dict()

    @abc.abstractmethod
    def pre_process(self):
        pass

    def to_dict(self) -> dict:
        self.pre_process()
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
