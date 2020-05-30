from abc import ABC

from JellyBot.api.static import result, param
from mongodb.factory import ChannelManager, RootUserManager
from flags import Platform

from JellyBot.api.responses.mixin import BaseMixin


class HandleChannelMixin(BaseMixin, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._channel_token = self._param_dict[param.Common.CHANNEL_TOKEN] = param_dict.get(param.Common.CHANNEL_TOKEN)

    def pre_process(self):
        super().pre_process()

        HandleChannelMixin._handle(self)

    def _handle(self):
        k = result.AutoReplyResponse.CHANNEL_OID
        if self._channel_token:
            self._flag[k] = self._channel_token
        else:
            self._err[k] = self._channel_token

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._channel_token


class HandlePlatformMixin(BaseMixin, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._platform = self._param_dict[param.Common.PLATFORM] = param_dict.get(param.Common.PLATFORM)

    def pre_process(self):
        super().pre_process()

        HandlePlatformMixin._handle(self)

    def _handle(self):
        k = result.AutoReplyResponse.PLATFORM
        if not self._platform:
            self._err[k] = None
        else:
            self._platform = self._flag[k] = Platform(int(self._platform))

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._platform is not None


class HandleChannelOidMixin(BaseMixin, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._param_dict.update(**{
            param.Common.CHANNEL_OID: param_dict.get(param.Common.CHANNEL_OID)
        })

        self._channel_oid = self._param_dict[param.Common.CHANNEL_OID] = param_dict.get(param.Common.CHANNEL_OID)

    def _handle_channel_oid(self):
        if not self._channel_oid:
            self._err[param.Common.CHANNEL_OID] = self._channel_oid

    def pre_process(self):
        super().pre_process()

        self._handle_channel_oid()

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._channel_oid is not None


class HandleChannelRegisterOidMixin(HandleChannelMixin, HandlePlatformMixin, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

    def get_channel_oid(self):
        c = ChannelManager.ensure_register(self._platform, self._channel_token)
        if c.success:
            return c.model.id
        else:
            return None


class RequireSenderMixin(BaseMixin, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

    def _handle_sender_oid(self):
        if self._sender_oid is None:
            self._err[result.SenderIdentity.SENDER] = self._sender_oid

    def pre_process(self):
        super().pre_process()

        self._handle_sender_oid()

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._sender_oid is not None


class RequireSenderAutoRegisterMixin(RequireSenderMixin, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        RequireSenderAutoRegisterMixin._handle_sender_oid_this(self, param_dict)

    def _handle_sender_oid_this(self, param_dict):
        RequireSenderAutoRegisterMixin._handle_api_token(self, param_dict)

        if self._sender_oid is None:
            self._err[result.SenderIdentity.SENDER] = self._sender_oid

    def _handle_api_token(self, param_dict):
        api_token = param_dict.get(param.Common.API_TOKEN)
        if api_token is not None:
            rt_result = RootUserManager.get_root_data_api_token(api_token, skip_on_plat=True)
            if rt_result.success:
                self._sender_oid = rt_result.model.id
            else:
                RequireSenderAutoRegisterMixin._handle_user_token(self, param_dict)

    def _handle_user_token(self, param_dict):
        platform = param_dict.get(param.Common.PLATFORM)
        channel_token = param_dict.get(param.Common.CHANNEL_TOKEN)
        if platform is not None and channel_token is not None:
            rt_result = RootUserManager.get_root_data_onplat(platform, channel_token)
            if rt_result.success:
                self._sender_oid = rt_result.model.id

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._sender_oid is not None
