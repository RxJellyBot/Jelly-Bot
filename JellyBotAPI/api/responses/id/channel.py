from bson import ObjectId
from django.http import QueryDict

from JellyBotAPI.api.responses import BaseApiResponse
from JellyBotAPI.api.responses.mixin import (
    HandleChannelMixin, HandlePlatformMixin, RequireSenderMixin,
    SerializeErrorMixin, SerializeResultOnSuccessMixin, SerializeResultExtraMixin
)
from JellyBotAPI.api.static import param, result
from extutils import is_empty_string
from flags import TokenAction
from models import ChannelRegisterExistenceModel
from mongodb.factory import ChannelManager, TokenActionManager


class ChannelDataQueryResponse(HandleChannelMixin, HandlePlatformMixin, SerializeResultExtraMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

    def success_conditions(self) -> bool:
        return super().success_conditions() and self._result.success

    def process_ifnoerror(self):
        self._result = ChannelManager.get_channel_packed(self._platform, self._channel_token)

    def serialize_success(self) -> dict:
        return dict()

    def serialize_failed(self) -> dict:
        return dict()

    @property
    def param_dict(self) -> dict:
        return self._param_dict


class ChannelIssueRegisterTokenResponse(
        RequireSenderMixin, SerializeErrorMixin, SerializeResultOnSuccessMixin, BaseApiResponse):
    def __init__(self, param_dict, creator_oid):
        super().__init__(param_dict, creator_oid)

    def pre_process(self):
        super().pre_process()

    def process_ifnoerror(self):
        self._result = TokenActionManager.enqueue_action(
            self._sender_oid, TokenAction.CONNECT_CHANNEL,
            ChannelRegisterExistenceModel, RootOid=self._sender_oid)
