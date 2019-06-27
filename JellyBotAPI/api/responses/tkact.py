from extutils import is_empty_string
from JellyBotAPI.api.static import param, result
from JellyBotAPI.api.responses.mixin import SerializeErrorMixin
from mongodb.factory import TokenActionManager

from ._base import BaseApiResponse


class TokenActionCompleteApiResponse(SerializeErrorMixin, BaseApiResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

        self._token = param_dict.get(param.TokenAction.TOKEN)
        self._param_dict.update(**param_dict)

    def success_conditions(self) -> bool:
        return not is_empty_string(self._token) and self._result.success

    def pre_process(self):
        self._result = TokenActionManager.complete_action(self._token, self._param_dict)
        if not self._result.success:
            self._err[result.TokenActionResponse.COMPLETION_RESULT] = self._result

    def process_ifnoerror(self):
        pass

    def serialize_success(self) -> dict:
        return {result.RESULT: self._result}

    def serialize_failed(self) -> dict:
        return {result.ERRORS: self._err}


class TokenActionListApiResponse(SerializeErrorMixin, BaseApiResponse):
    def __init__(self, param_dict, sender_oid):
        super().__init__(param_dict, sender_oid)

    def success_conditions(self) -> bool:
        return self._sender_oid is not None

    def _handle_creator_oid_(self):
        if not self._sender_oid:
            self._err[result.TokenActionResponse.CREATOR_OID] = None

    def pre_process(self):
        self._handle_creator_oid_()

    def process_ifnoerror(self):
        self._result = list(TokenActionManager.get_queued_actions(self._sender_oid))

    def serialize_success(self) -> dict:
        return {result.RESULT: self._result}
