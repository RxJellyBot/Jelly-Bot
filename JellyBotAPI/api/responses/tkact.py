from django.http import QueryDict

from extutils import is_empty_string
from JellyBotAPI.api.static import param, result
from flags import Platform
from mongodb.factory import TokenActionManager, MixedUserManager
from mongodb.factory.results import OperationOutcome

from ._base import BaseApiResponse


class TokenActionCompleteApiResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)

        self._token = param_dict.get(param.TokenAction.TOKEN)
        self._param_dict = param_dict

    def is_success(self) -> bool:
        return not is_empty_string(self._token) and OperationOutcome.is_success(self._result.outcome)

    def pre_process(self):
        self._result = TokenActionManager.complete_action(self._token, self._param_dict)

    def process_ifnoerror(self):
        pass

    def serialize_success(self) -> dict:
        return {result.RESULT: self._result}

    def serialize_failed(self) -> dict:
        return dict()


class TokenActionListApiResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)
        self._param_dict = {
            param.TokenAction.USER_TOKEN: param_dict.get(param.TokenAction.USER_TOKEN),
            param.TokenAction.PLATFORM: param_dict.get(param.TokenAction.PLATFORM)
        }

        self._platform = self._param_dict[param.TokenAction.PLATFORM]
        self._user_token = self._param_dict[param.TokenAction.USER_TOKEN]
        self._creator_oid = None

    def _handle_platform(self):
        if self._platform is not None:
            self._platform = Platform(int(self._platform))

    def is_success(self) -> bool:
        return super().is_success() and \
               self._platform is not None and \
               not is_empty_string(self._user_token) and \
               self._creator_oid is not None

    def _handle_get_creator_oid(self):
        self._creator_oid = MixedUserManager.get_user_data_on_plat(self._platform, self._user_token)
        if self._creator_oid:
            self._creator_oid = self._creator_oid.id.value
        else:
            self._err[result.TokenActionResponse.CREATOR_OID] = None

    def pre_process(self):
        self._handle_platform()
        self._handle_get_creator_oid()

    def process_ifnoerror(self):
        self._result = list(TokenActionManager.get_queued_actions(self._creator_oid))

    def serialize_success(self) -> dict:
        return {result.RESULT: self._result}

    def serialize_failed(self) -> dict:
        return {result.ERRORS: self._err}
