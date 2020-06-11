from dataclasses import dataclass
from typing import Optional, Union, Dict, Any

from JellyBot.api.static import result
from models import ChannelProfileModel

from ._outcome import OperationOutcome, WriteOutcome, GetOutcome
from ._base import ModelResult, BaseResult


@dataclass
class GetPermissionProfileResult(ModelResult):
    outcome: GetOutcome
    exception: Optional[Exception] = None
    model: Optional[ChannelProfileModel] = None


@dataclass
class CreateProfileResult(ModelResult):
    outcome: WriteOutcome
    exception: Optional[Exception] = None
    model: Optional[ChannelProfileModel] = None


@dataclass
class RegisterProfileResult(ModelResult):
    """
    .. note::
        ``outcome`` will be
            :class:`WriteOutcome` if ``ProfileManager.register_new()`` is being called.

            :class:`GetOutcome` if ``ProfileManager.register_new_default()`` is being called.
    """
    outcome: Union[WriteOutcome, GetOutcome]
    exception: Optional[Exception] = None
    model: Optional[ChannelProfileModel] = None
    attach_outcome: OperationOutcome = OperationOutcome.X_NOT_EXECUTED
    parse_arg_outcome: Optional[OperationOutcome] = None


@dataclass
class ArgumentParseResult(BaseResult):
    outcome: OperationOutcome
    exception: Optional[Exception] = None
    parsed_args: Optional[Dict[str, Any]] = None

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Results.MODEL: self.parsed_args})
        return d
