from dataclasses import dataclass
from datetime import datetime

from JellyBotAPI.api.static import result

from ._base import BaseResult
from ._outcome import InsertOutcome


@dataclass
class EnqueueTokenActionResult(BaseResult):
    def __init__(self, outcome, token, expiry, exception=None):
        """
        :type outcome: InsertOutcome
        :type token: str
        :type expiry: datetime
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, exception)
        self._token = token
        self._expiry = expiry

    @property
    def token(self) -> str:
        return self._token

    @property
    def expiry(self) -> datetime:
        return self._expiry

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Results.TOKEN: self._token,
                    result.Results.EXPIRY: self._expiry})
        return d
