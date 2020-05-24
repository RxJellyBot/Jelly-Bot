from abc import ABC
from dataclasses import dataclass
from typing import List, Optional

from JellyBot.api.static import result
from models import OnPlatformUserModel, APIUserModel, RootUserModel

from ._base import ModelResult
from ._outcome import WriteOutcome


@dataclass
class IdentityRegistrationResult(ModelResult, ABC):
    pass


@dataclass
class OnSiteUserRegistrationResult(IdentityRegistrationResult):
    model: Optional[APIUserModel]
    token: Optional[str]

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.UserManagementResponse.TOKEN: self.token})
        return d


@dataclass
class OnPlatformUserRegistrationResult(IdentityRegistrationResult):
    model: Optional[OnPlatformUserModel]


@dataclass
class GetRootUserDataResult(ModelResult):
    model: Optional[RootUserModel]
    model_api: Optional[APIUserModel] = None
    model_onplat_list: Optional[List[OnPlatformUserModel]] = None


@dataclass
class RootUserRegistrationResult(ModelResult):
    model: Optional[RootUserModel]
    conn_outcome: WriteOutcome
    idt_reg_result: IdentityRegistrationResult
    hint: str

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{
            result.UserManagementResponse.CONN_OUTCOME:
                self.conn_outcome,
            result.UserManagementResponse.REG_RESULT:
                self.idt_reg_result.serialize() if self.idt_reg_result else None,
            result.UserManagementResponse.HINT:
                self.hint
        })
        return d


@dataclass
class RootUserUpdateResult(ModelResult):
    model: Optional[RootUserModel]
