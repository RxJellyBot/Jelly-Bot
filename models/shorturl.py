import os
from datetime import datetime

from models import ModelDefaultValueExt, Model
from models.field import (
    TextField, UrlField, ArrayField, ObjectIDField, BooleanField
)


class ShortUrlRecordModel(Model):
    # CHANGE THE KEY NAME AS WELL FOR github.com/RaenonX/Jelly-Bot-ShortURL IF CHANGING THE KEY NAME OF THESE FIELDS
    Code = TextField("cd", default=ModelDefaultValueExt.Required)
    Target = UrlField("tgt", default=ModelDefaultValueExt.Required)
    CreatorOid = ObjectIDField("cr", default=ModelDefaultValueExt.Required, stores_uid=True)
    UsedTimestamp = ArrayField("ts", datetime)
    Disabled = BooleanField("d", default=False)

    @property
    def used_count(self) -> int:
        return len(self.used_timestamp)

    @property
    def short_url(self) -> str:
        return f"{os.environ['SERVICE_SHORT_URL']}/{self.code}"
