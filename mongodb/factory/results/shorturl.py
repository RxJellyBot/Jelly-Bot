from dataclasses import dataclass
from typing import Optional

from JellyBot.api.static import result
from models import ShortUrlRecordModel

from ._base import ModelResult


@dataclass
class UrlShortenResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[ShortUrlRecordModel] = None

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Service.ShortUrl.SHORTENED_URL: self.model.short_url if self.model else None})
        return d
