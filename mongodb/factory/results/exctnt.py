from dataclasses import dataclass

from bson import ObjectId

from ._base import ModelResult
from ._outcome import WriteOutcome


@dataclass
class RecordExtraContentResult(ModelResult):
    def __init__(self, outcome, model=None, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: Optional[ExtraContentModel]
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)

    @property
    def model_id(self) -> ObjectId:
        return self.model.id
