from dataclasses import dataclass

from models import ChannelModel

from ._base import ModelResult
from ._outcome import WriteOutcome, GetOutcome, OperationOutcome


@dataclass
class ChannelRegistrationResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: ChannelModel or None
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
class ChannelChangeNameResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: OperationOutcome
        :type model: ChannelModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


@dataclass
class ChannelCollectionRegistrationResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: ChannelCollectionModel or None
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)
