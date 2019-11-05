from dataclasses import dataclass

from JellyBot.api.static import result
from models import ShortUrlRecordModel
from ._outcome import WriteOutcome
from ._base import ModelResult


@dataclass
class UrlShortenResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: ShortUrlRecordModel or None
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Service.ShortUrl.SHORTENED_URL: self._model.short_url if self._model else None})
        return d
