import os
from datetime import datetime

from models import ModelDefaultValueExt, Model
from models.field import (
    TextField, UrlField, ArrayField, ObjectIDField, BooleanField
)
from strres.models import ShortUrl


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
        root_url = os.environ.get("SERVICE_SHORT_URL")
        if not root_url:
            return ShortUrl.SERVICE_NOT_AVAILABLE

        return f"{root_url}/{self.code}"
