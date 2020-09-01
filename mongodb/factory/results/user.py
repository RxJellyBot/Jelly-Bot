"""Result objects for user management."""
from abc import ABC
from dataclasses import dataclass
from typing import List, Optional

from JellyBot.api.static import result
from models import OnPlatformUserModel, APIUserModel, RootUserModel

from ._base import ModelResult
from ._outcome import WriteOutcome


@dataclass
class IdentityRegistrationResult(ModelResult, ABC):
    """Base class for user identity registration result."""


@dataclass
class APIUserRegistrationResult(IdentityRegistrationResult):
    """API user registration result object."""

    model: Optional[APIUserModel]
    token: Optional[str]

    def serialize(self) -> dict:
        dict_ = super().serialize()
        dict_.update(**{result.UserManagementResponse.TOKEN: self.token})
        return dict_


@dataclass
class OnPlatformUserRegistrationResult(IdentityRegistrationResult):
    """On-platform user registration result object."""

    model: Optional[OnPlatformUserModel]


@dataclass
class GetRootUserDataResult(ModelResult):
    """Result of getting the root user data."""

    model: Optional[RootUserModel]
    model_api: Optional[APIUserModel] = None
    model_onplat_list: Optional[List[OnPlatformUserModel]] = None


@dataclass
class RootUserRegistrationResult(ModelResult):
    """Result of registrating the root user."""

    model: Optional[RootUserModel]
    conn_outcome: WriteOutcome
    idt_reg_result: IdentityRegistrationResult

    def serialize(self) -> dict:
        dict_ = super().serialize()
        dict_.update(**{
            result.UserManagementResponse.CONN_OUTCOME:
                self.conn_outcome,
            result.UserManagementResponse.REG_RESULT:
                self.idt_reg_result.serialize() if self.idt_reg_result else None
        })
        return dict_


@dataclass
class RootUserUpdateResult(ModelResult):
    """Result of updating the root user properties."""

    model: Optional[RootUserModel]
