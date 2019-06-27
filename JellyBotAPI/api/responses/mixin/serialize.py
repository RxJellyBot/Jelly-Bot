from abc import ABC

from JellyBotAPI.api.static import result
from JellyBotAPI.api.responses import BaseApiResponse


class SerializeErrorMixin(BaseApiResponse, ABC):
    def serialize_failed(self) -> dict:
        d = super().serialize_failed()
        d[result.ERRORS] = self._err
        return d
