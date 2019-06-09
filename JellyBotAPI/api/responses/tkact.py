from django.http import QueryDict

from JellyBotAPI.api.static import param, result
from mongodb.factory import TokenActionManager
from mongodb.factory.results import OperationOutcome

from ._base import BaseApiResponse


class TokenActionApiResponse(BaseApiResponse):
    def __init__(self, param_dict: QueryDict):
        super().__init__(param_dict)

        self._token = param_dict.get(param.TokenAction.TOKEN)
        self._param_dict = param_dict

    def is_success(self) -> bool:
        return self._token is not None and OperationOutcome.is_success(self._result.outcome)

    def pre_process(self):
        pass

    def process_ifnoerror(self):
        self._result = TokenActionManager.complete_action(self._token, self._param_dict)

    def serialize_success(self) -> dict:
        return {result.RESULT: self._result}

    def serialize_failed(self) -> dict:
        return dict()
