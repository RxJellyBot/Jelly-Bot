from dataclasses import dataclass
from typing import Optional

from bson import ObjectId
from django.urls import reverse

from models import Model
from JellyBot.systemconfig import HostUrl

from ._base import ModelResult


@dataclass
class RecordExtraContentResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[Model] = None

    @property
    def model_id(self) -> Optional[ObjectId]:
        if self.model:
            return self.model.id
        else:
            return None

    @property
    def url(self) -> str:
        return f'{HostUrl}{reverse("page.extra", kwargs={"page_id": str(self.model_id)})}'
