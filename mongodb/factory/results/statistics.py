from dataclasses import dataclass

from models import APIStatisticModel
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
