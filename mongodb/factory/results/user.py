from abc import ABC

from JellyBotAPI.api.static import result
from models import MixedUserModel, OnPlatformUserModel, APIUserModel

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
        d.update(**{result.Results.TOKEN: self._token})
        return d


class GetOnSiteUserDataResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: GetOutcome
        :type model: APIUserModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


class OnPlatformUserRegistrationResult(IdentityRegistrationResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: InsertOutcome
        :type model: OnPlatformUserModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


class MixedUserRegistrationResult(ModelResult):
    def __init__(self, overall_outcome, conn_entry, conn_outcome, conn_ex, idt_reg_result, hint):
        """
        :type overall_outcome: InsertOutcome
        :type conn_entry: MixedUserModel
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
        d.update(**{result.Results.CONN_OUTCOME: self._conn_outcome,
                    result.Results.REG_RESULT: self._idt_reg_result,
                    result.Results.HINT: self._hint})
        return d
