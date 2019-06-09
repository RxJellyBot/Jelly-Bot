from django.http import QueryDict

from JellyBotAPI.api.static import param, result
from extutils import cast_keep_none
from flags import Platform
from mongodb.factory import ChannelManager
from mongodb.factory.results import GetOutcome

from ._base import BaseApiResponse


class ChannelDataQueryResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)
        self._param_dict = {
            param.DataQuery.Channel.CHANNEL_TOKEN: param_dict.get(param.DataQuery.Channel.CHANNEL_TOKEN),
            param.DataQuery.Channel.PLATFORM: cast_keep_none(param_dict.get(param.DataQuery.Channel.PLATFORM), int)
        }

        self._channel = self._param_dict[param.DataQuery.Channel.CHANNEL_TOKEN]
        self._platform = self._param_dict[param.DataQuery.Channel.PLATFORM]

    def is_success(self) -> bool:
        return self._channel is not None and \
               self._platform is not None and \
               GetOutcome.is_success(self._result.outcome)

    # noinspection PyArgumentList
    def _handle_platform(self):
        if self._platform is not None:
            self._platform = Platform(self._platform)

    def pre_process(self):
        self._handle_platform()

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
