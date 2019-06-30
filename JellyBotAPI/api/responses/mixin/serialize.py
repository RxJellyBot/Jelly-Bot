from abc import ABC

from JellyBotAPI.api.static import result
from JellyBotAPI.api.responses.mixin import BaseMixin


class SerializeErrorMixin(BaseMixin, ABC):
    def serialize_failed(self) -> dict:
        d = super().serialize_failed()
        d[result.ERRORS] = self._err
        return d


class SerializeResultOnSuccessMixin(BaseMixin, ABC):
    def serialize_success(self) -> dict:
        d = super().serialize_success()
        d[result.RESULT] = self._result
        return d


class SerializeResultExtraMixin(BaseMixin, ABC):
    def serialize_extra(self) -> dict:
        d = super().serialize_extra()
        d[result.RESULT] = self._result
        return d
