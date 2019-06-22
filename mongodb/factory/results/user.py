from abc import ABC

from JellyBotAPI.api.static import result
from models import RootUserModel, OnPlatformUserModel, APIUserModel

from ._base import ModelResult
from ._outcome import InsertOutcome


class IdentityRegistrationResult(ModelResult, ABC):
    pass


class OnSiteUserRegistrationResult(IdentityRegistrationResult):
    def __init__(self, outcome, model, exception=None, token=None):
        """
        :type outcome: InsertOutcome
        :type model: APIUserModel
        :type exception: Optional[Exception]
        :type token: str
        """
        super().__init__(outcome, model, exception)
        self._token = token

    @property
    def token(self) -> str:
        return self._token

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.UserManagementResponse.TOKEN: self._token})
        return d


class OnPlatformUserRegistrationResult(IdentityRegistrationResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: InsertOutcome
        :type model: OnPlatformUserModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


class GetRootUserDataResult(ModelResult):
    def __init__(self, outcome, model_root, exception=None):
        """
        :type outcome: GetOutcome
        :type model_root: RootUserModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model_root, exception)


class GetRootUserDataApiResult(GetRootUserDataResult):
    def __init__(self, outcome, model_root, model_api, exception=None):
        """
        :type outcome: GetOutcome
        :type model_root: RootUserModel
        :type model_api: APIUserModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model_root, exception)
        self._model_api = model_api

    @property
    def model_api(self) -> APIUserModel:
        return self._model_api


class RootUserRegistrationResult(ModelResult):
    def __init__(self, overall_outcome, conn_entry, conn_outcome, conn_ex, idt_reg_result, hint):
        """
        :type overall_outcome: InsertOutcome
        :type conn_entry: RootUserModel
        :type conn_outcome: InsertOutcome
        :type conn_ex: Optional[Exception]
        :type idt_reg_result: IdentityRegistrationResult
        :type hint: str
        """
        super().__init__(overall_outcome, conn_entry, conn_ex)
        self._conn_outcome = conn_outcome
        self._idt_reg_result = idt_reg_result
        self._hint = hint

    @property
    def idt_reg_result(self) -> IdentityRegistrationResult:
        return self._idt_reg_result

    @property
    def conn_outcome(self) -> InsertOutcome:
        return self._conn_outcome

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.UserManagementResponse.CONN_OUTCOME: self._conn_outcome,
                    result.UserManagementResponse.REG_RESULT: self._idt_reg_result,
                    result.UserManagementResponse.HINT: self._hint})
        return d


class RootUserUpdateResult(ModelResult):
    pass
