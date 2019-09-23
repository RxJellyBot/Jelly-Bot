from dataclasses import dataclass

from models import ExtraContentModel

from ._base import ModelResult
from ._outcome import WriteOutcome


@dataclass
class RecordExtraContentResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: ExtraContentModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)

    @property
    def model_id(self):
        return self.model.id
