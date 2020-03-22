from abc import ABC
from typing import Set

from JellyBot.api.static import result
from JellyBot.api.responses.mixin import RequireSenderMixin, HandleChannelOidMixin
from mongodb.factory import ProfileManager
from flags import ProfilePermission


class RequirePermissionMixin(RequireSenderMixin, HandleChannelOidMixin, ABC):
    @staticmethod
    def required_permission() -> Set[ProfilePermission]:
        raise NotImplementedError()

    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

    def _permission_check_(self):
        permission_pass = ProfileManager.get_user_permissions(self._channel_oid, self._sender_oid)\
            .issuperset(self.required_permission())

        if not permission_pass:
            self._err[result.SenderIdentity.PERMISSION] = False

    def pre_process(self):
        super().pre_process()

        self._permission_check_()
