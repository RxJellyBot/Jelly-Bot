from abc import ABC

from bson import ObjectId

from flags import ProfilePermission
from JellyBot.api.responses import BaseApiResponse
from JellyBot.api.static import param
from JellyBot.api.responses.mixin import (
    RequireSenderMixin, HandleChannelOidMixin,
    SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin
)
from extutils import safe_cast
from mongodb.factory import ProfileManager
from mongodb.factory.results import OperationOutcome, WriteOutcome


class PermissionQueryResponse(
        RequireSenderMixin, HandleChannelOidMixin,
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

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._root_oid is not None

    def is_success(self) -> bool:
        return super().is_success() and self._profiles is not None

    def process_pass(self):
        self._profiles = ProfileManager.get_user_profiles(self._channel_oid, self._root_oid)

        if self._profiles:
            self._result = ProfileManager.get_permissions(self._profiles)


class ProfileResponseBase(
        RequireSenderMixin, HandleChannelOidMixin,
        SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin, BaseApiResponse, ABC):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._param_dict.update(**{
            param.Manage.USER_OID: sender_oid,
            param.Manage.Profile.PROFILE_OID: param_dict.get(param.Manage.Profile.PROFILE_OID),
            param.Manage.Profile.TARGET: param_dict.get(param.Manage.Profile.TARGET),
        })

        self._profile_oid = self._param_dict[param.Manage.Profile.PROFILE_OID]
        self._target_oid = self._param_dict[param.Manage.Profile.TARGET] or self._sender_oid
        self._target_self = self._sender_oid == self._target_oid

        self._permissions = ProfileManager.get_user_permissions(self._channel_oid, self._sender_oid)

    def _handle_profile_oid_(self):
        self._profile_oid = safe_cast(self._profile_oid, ObjectId)
        if not self._profile_oid:
            self._err[param.Manage.Profile.PROFILE_OID] = self._profile_oid

    def pre_process(self):
        super().pre_process()

        self._handle_profile_oid_()

    def pass_condition(self) -> bool:
        return super().pass_condition() and self._profile_oid is not None and self._sender_oid is not None

    def is_success(self) -> bool:
        return super().is_success() and self._result.is_success

    @property
    def permitted(self):
        if self._target_self:
            return ProfilePermission.PRF_CONTROL_SELF in self._permissions
        else:
            return ProfilePermission.PRF_CONTROL_MEMBER in self._permissions


class ProfileAttachResponse(ProfileResponseBase):
    def process_pass(self):
        if self.permitted:
            model_result = ProfileManager.attach_profile(self._target_oid, self._channel_oid, self._profile_oid)
            self._result = OperationOutcome.O_COMPLETED if model_result is not None else OperationOutcome.X_ERROR
        else:
            self._result = OperationOutcome.X_INSUFFICIENT_PERMISSION


class ProfileDetachResponse(ProfileResponseBase):
    def process_pass(self):
        if self.permitted:
            self._result = ProfileManager.detach_profile(self._profile_oid, self._target_oid)
        else:
            self._result = WriteOutcome.X_INSUFFICIENT_PERMISSION


class ProfileNameCheckResponse(
        HandleChannelOidMixin,
        SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin, BaseApiResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._param_dict.update(**{
            param.Manage.Profile.NAME: param_dict.get(param.Manage.Profile.NAME)
        })

        self._profile_name = self._param_dict[param.Manage.Profile.NAME]

    def process_pass(self):
        self._result = ProfileManager.is_name_available(self._channel_oid, self._profile_name)
