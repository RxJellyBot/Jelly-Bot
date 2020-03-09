from dataclasses import dataclass

from bson import ObjectId
from django.urls import reverse

from JellyBot.systemconfig import HostUrl

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

    @property
    def url(self) -> str:
        return f'{HostUrl}{reverse("page.extra", kwargs={"page_id": str(self.model_id)})}'
