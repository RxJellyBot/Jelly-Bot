from dataclasses import dataclass

from ._base import ModelResult
from ._outcome import GetOutcome, WriteOutcome


@dataclass
class GetPermissionProfileResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: GetOutcome
        :type model: Optional[ChannelPermissionProfileModel]
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


@dataclass
class CreateProfileResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: Optional[ChannelProfileModel]
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)
