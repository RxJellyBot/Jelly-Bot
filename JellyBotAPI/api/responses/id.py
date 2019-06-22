from JellyBotAPI.api.static import result
from mongodb.factory import ChannelManager

from ._base import BaseApiResponse
from ._mixin import HandleChannelMixin, HandlePlatformMixin


class ChannelDataQueryResponse(HandleChannelMixin, HandlePlatformMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

    def extra_success_conditions(self) -> bool:
        return super().extra_success_conditions() and self._result.success

    def process_ifnoerror(self):
        self._result = ChannelManager.get_channel_packed(self._platform, self._channel)

    def serialize_success(self) -> dict:
        return dict()

    def serialize_failed(self) -> dict:
        return dict()

    def serialize_extra(self) -> dict:
        return {result.RESULT: self._result}

    @property
    def param_dict(self) -> dict:
        return self._param_dict
