from dataclasses import dataclass

from models import ChannelModel

from ._base import ModelResult
from ._outcome import InsertOutcome, GetOutcome


@dataclass
class ChannelRegistrationResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: InsertOutcome
        :type model: ChannelModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


@dataclass
class ChannelGetResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: GetOutcome
        :type model: ChannelModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


@dataclass
class PermissionProfileRegistrationResult(ModelResult):
    # FIXME: `PermissionProfileRegistrationResult` not completed
    def __init__(self):
        super().__init__()
