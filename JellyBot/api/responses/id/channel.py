from JellyBot.api.responses import BaseApiResponse
from JellyBot.api.static import param
from JellyBot.api.responses.mixin import (
    HandleChannelMixin, HandlePlatformMixin, RequireSenderMixin,
    SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin
)
from flags import Execode
from mongodb.factory import ChannelManager, ExecodeManager


class ChannelDataQueryResponse(HandleChannelMixin, HandlePlatformMixin, SerializeResultExtraMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._result.success

    def process_pass(self):
        self._result = ChannelManager.get_channel_packed(self._platform, self._channel_token)

    def serialize_success(self) -> dict:
        return dict()

    def serialize_failed(self) -> dict:
        return dict()

    @property
    def param_dict(self) -> dict:
        return self._param_dict


class ChannelIssueRegisterExecodeResponse(
        RequireSenderMixin, SerializeErrorMixin, SerializeResultOnSuccessMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

    def pre_process(self):
        super().pre_process()

    def process_pass(self):
        self._result = ExecodeManager.enqueue_execode(self._sender_oid, Execode.REGISTER_CHANNEL)


class ChannelNameChangeResponse(
        RequireSenderMixin, SerializeErrorMixin, SerializeResultOnSuccessMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

        self._param_dict.update(**{
            param.Manage.USER_OID: creator_oid,
            param.Manage.Channel.CHANNEL_OID: param_dict.get(param.Manage.Channel.CHANNEL_OID),
            param.Manage.Channel.NEW_NAME: param_dict.get(param.Manage.Channel.NEW_NAME)
        })

        self._root_oid = creator_oid
        self._channel_oid = self._param_dict[param.Manage.Channel.CHANNEL_OID]
        self._new_name = self._param_dict[param.Manage.Channel.NEW_NAME]

    def pre_process(self):
        super().pre_process()

    def process_pass(self):
        self._result = ChannelManager.update_channel_nickname(self._channel_oid, self._root_oid, self._new_name)
