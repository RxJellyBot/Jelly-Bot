from abc import ABC

from JellyBotAPI.api.static import result, param
from JellyBotAPI.api.responses import BaseApiResponse
from mongodb.factory import ChannelManager
from extutils import is_empty_string
from flags import Platform



class HandleChannelMixin(BaseApiResponse, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._channel_token = self._param_dict[param.Common.CHANNEL_TOKEN] = param_dict.get(param.Common.CHANNEL_TOKEN)

    def pre_process(self):
        super().pre_process()

        HandleChannelMixin._handle_(self)

    def _handle_(self):
        k = result.AutoReplyResponse.CHANNEL_OID
        if is_empty_string(self._channel_token):
            self._err[k] = self._channel_token
        else:
            self._flag[k] = self._channel_token

    def success_conditions(self) -> bool:
        return super().success_conditions() and \
               self._channel_token is not None and \
               not is_empty_string(self._channel_token)


class HandlePlatformMixin(BaseApiResponse, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._platform = self._param_dict[param.Common.PLATFORM] = param_dict.get(param.Common.PLATFORM)

    def pre_process(self):
        super().pre_process()

        HandlePlatformMixin._handle_(self)

    # noinspection PyArgumentList
    def _handle_(self):
        k = result.AutoReplyResponse.PLATFORM
        if self._platform is None:
            self._err[k] = None
        else:
            self._platform = self._flag[k] = Platform(int(self._platform))

    def success_conditions(self) -> bool:
        return super().success_conditions() and \
               self._platform is not None


class HandleChannelOidMixin(HandleChannelMixin, HandlePlatformMixin, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

    def get_channel_oid(self):
        c = ChannelManager.register(self._platform, self._channel_token)
        if c.success:
            return c.model.id
        else:
            return None
