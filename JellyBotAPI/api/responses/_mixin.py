from abc import ABC

from JellyBotAPI.api.static import result, param
from extutils import is_empty_string
from flags import Platform

from ._base import BaseApiResponse


class HandleChannelMixin(BaseApiResponse, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._channel = self._param_dict[param.Common.CHANNEL_TOKEN] = param_dict.get(param.Common.CHANNEL_TOKEN)

    def pre_process(self):
        self._handle_()

        super().pre_process()

    def _handle_(self):
        k = result.Common.CHANNEL_OID
        if self._channel is None:
            self._err[k] = None
        else:
            self._flag[k] = self._channel

    def extra_success_conditions(self) -> bool:
        return super().extra_success_conditions() and \
               self._channel is not None and \
               not is_empty_string(self._channel)


class HandlePlatformMixin(BaseApiResponse, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._platform = self._param_dict[param.Common.PLATFORM] = param_dict.get(param.Common.PLATFORM)

    def pre_process(self):
        self._handle_()

        super().pre_process()

    # noinspection PyArgumentList
    def _handle_(self):
        k = result.Common.PLATFORM
        if self._platform is None:
            self._err[k] = None
        else:
            self._platform = self._flag[k] = Platform(int(self._platform))

    def extra_success_conditions(self) -> bool:
        return super().extra_success_conditions() and \
               self._platform is not None
