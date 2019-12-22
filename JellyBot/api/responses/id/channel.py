from bson import ObjectId

from extutils.boolext import str_to_bool
from extutils import safe_cast
from JellyBot.api.responses import BaseApiResponse
from JellyBot.api.static import param
from JellyBot.api.responses.mixin import (
    HandleChannelMixin, HandlePlatformMixin, RequireSenderMixin,
    SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin
)
from flags import Execode
from mongodb.factory import ChannelManager, ExecodeManager, ProfileManager


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


class ChannelStarChangeResponse(
        RequireSenderMixin, SerializeErrorMixin, SerializeResultOnSuccessMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

        self._param_dict.update(**{
            param.Manage.USER_OID: creator_oid,
            param.Manage.Channel.CHANNEL_OID: param_dict.get(param.Manage.Channel.CHANNEL_OID),
            param.Manage.Channel.STAR: param_dict.get(param.Manage.Channel.STAR)
        })

        self._root_oid = creator_oid
        self._channel_oid = self._param_dict[param.Manage.Channel.CHANNEL_OID]
        self._star = self._param_dict[param.Manage.Channel.STAR]

    def pre_process(self):
        super().pre_process()

        self._handle_star_()
        self._handle_channel_oid_()

    def _handle_channel_oid_(self):
        self._channel_oid = safe_cast(self._channel_oid, ObjectId)

    def _handle_star_(self):
        self._star = str_to_bool(self._star).to_bool()

    def process_pass(self):
        self._result = ProfileManager.change_channel_star(self._channel_oid, self._root_oid, self._star)

    def is_success(self) -> bool:
        return super().is_success() and self._result
