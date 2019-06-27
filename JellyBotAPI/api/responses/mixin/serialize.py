from abc import ABC

from JellyBotAPI.api.static import result
from JellyBotAPI.api.responses.mixin import BaseMixin


class SerializeErrorMixin(BaseMixin, ABC):
    def serialize_failed(self) -> dict:
        d = super().serialize_failed()
        d[result.ERRORS] = self._err
        return d
