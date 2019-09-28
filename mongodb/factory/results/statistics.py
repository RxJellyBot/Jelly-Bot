from dataclasses import dataclass

from models import APIStatisticModel, MessageRecordModel
from ._outcome import WriteOutcome
from ._base import ModelResult


@dataclass
class RecordAPIStatisticsResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: APIStatisticModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


@dataclass
class MessageRecordResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: MessageRecordModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)
