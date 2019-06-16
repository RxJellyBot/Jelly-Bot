from dataclasses import dataclass
from datetime import datetime

from JellyBotAPI.api.static import result
from models import TokenActionModel

from ._base import BaseResult, ModelResult
from ._outcome import InsertOutcome, OperationOutcome


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


@dataclass
class CompleteTokenActionResult(ModelResult):
    def __init__(self, outcome, action_model, lacking_keys, exception=None):
        """
        :type outcome: OperationOutcome
        :type action_model: TokenActionModel
        :type lacking_keys: set
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, action_model, exception)
        self._lacking_keys = lacking_keys

    @property
    def lacking_keys(self) -> set:
        return self._lacking_keys

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Results.LACKING_KEYS: self._lacking_keys})
        return d
