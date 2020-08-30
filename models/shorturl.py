"""Models for Short URL service."""
import os
from datetime import datetime

from models import ModelDefaultValueExt, Model
from models.field import (
    TextField, UrlField, ArrayField, ObjectIDField, BooleanField
)
from strres.models import ShortUrl


class ShortUrlRecordModel(Model):
    """Model for a short URL record entry."""

    # CHANGE THE KEY NAME AS WELL FOR github.com/RxJellyBot/Jelly-Bot-ShortURL
    # IF CHANGING THE KEY NAME OF THESE FIELDS
    Code = TextField("cd", default=ModelDefaultValueExt.Required)
    Target = UrlField("tgt", default=ModelDefaultValueExt.Required)
    CreatorOid = ObjectIDField("cr", default=ModelDefaultValueExt.Required, stores_uid=True)
    UsedTimestamp = ArrayField("ts", datetime)
    Disabled = BooleanField("d", default=False)

    @property
    def used_count(self) -> int:
        """
        Get the count of how many times this short URL has been called.

        :return: count of times that this short URL been called
        """
        return len(self.used_timestamp)

    @property
    def short_url(self) -> str:
        """
        Get the complete URL of this short URL.

        :return: complete URL of this short URL
        """
        root_url = os.environ.get("SERVICE_SHORT_URL")
        if not root_url:
            return ShortUrl.SERVICE_NOT_AVAILABLE

        return f"{root_url}/{self.code}"
