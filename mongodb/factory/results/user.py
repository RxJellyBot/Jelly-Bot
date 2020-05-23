from abc import ABC
from dataclasses import dataclass
from typing import List, Optional

from JellyBot.api.static import result
from models import OnPlatformUserModel, APIUserModel

from ._base import ModelResult
from ._outcome import WriteOutcome


@dataclass
class IdentityRegistrationResult(ModelResult, ABC):
    pass


@dataclass
class OnSiteUserRegistrationResult(IdentityRegistrationResult):
    token: Optional[str]

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.UserManagementResponse.TOKEN: self.token})
        return d


@dataclass
class OnPlatformUserRegistrationResult(IdentityRegistrationResult):
    pass


@dataclass
class GetRootUserDataResult(ModelResult):
    pass


@dataclass
class GetRootUserDataApiResult(GetRootUserDataResult):
    model_api: APIUserModel
    model_onplat_list: List[OnPlatformUserModel]


@dataclass
class RootUserRegistrationResult(ModelResult):
    conn_outcome: WriteOutcome
    idt_reg_result: IdentityRegistrationResult
    hint: str

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.UserManagementResponse.CONN_OUTCOME: self.conn_outcome,
                    result.UserManagementResponse.REG_RESULT: self.idt_reg_result.serialize(),
                    result.UserManagementResponse.HINT: self.hint})
        return d


@dataclass
class RootUserUpdateResult(ModelResult):
    pass
