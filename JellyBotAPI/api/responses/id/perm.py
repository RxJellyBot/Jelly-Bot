from JellyBotAPI.api.responses import BaseApiResponse
from JellyBotAPI.api.static import param
from JellyBotAPI.api.responses.mixin import (
    RequireSenderMixin,
    SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin
)
from mongodb.factory import ProfileManager


class PermissionQueryResponse(
        RequireSenderMixin,
        SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin, BaseApiResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._param_dict.update(**{
            param.Manage.USER_OID: sender_oid,
            param.Manage.Channel.CHANNEL_OID: param_dict.get(param.Manage.Channel.CHANNEL_OID),
        })

        self._root_oid = sender_oid
        self._channel_oid = self._param_dict[param.Manage.Channel.CHANNEL_OID]
        self._profiles = None

    def _handle_channel_(self):
        if not self._channel_oid:
            self._err[param.Manage.Channel.CHANNEL_OID] = self._channel_oid

    def pre_process(self):
        super().pre_process()

        self._handle_channel_()

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._channel_oid is not None and self._root_oid is not None

    def is_success(self) -> bool:
        return super().is_success() and self._profiles is not None

    def process_pass(self):
        self._profiles = ProfileManager.get_user_profiles(self._channel_oid, self._root_oid)

        if self._profiles:
            self._result = ProfileManager.get_permissions(self._profiles)
