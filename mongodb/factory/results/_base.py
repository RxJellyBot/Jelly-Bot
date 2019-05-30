from abc import ABC
from typing import Optional

from JellyBotAPI.api.static import result
from models import Model

from ._outcome import BaseOutcome


class BaseResult(ABC):
    def __init__(self, outcome: BaseOutcome, exception=None):
        """
        :type outcome: BaseOutcome
        :param exception: Optional[Exception]
        """
        self._outcome = outcome
        self._exception = exception

    @property
    def outcome(self) -> BaseOutcome:
        return self._outcome

    @property
    def exception(self) -> Optional[Exception]:
        return self._exception

    def serialize(self) -> dict:
        return {result.Results.EXCEPTION: str(self._exception), result.Results.OUTCOME: int(self._outcome)}


class ModelResult(BaseResult, ABC):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: BaseOutcome
        :type model: Model
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, exception)
        self._model = model

    @property
    def model(self) -> Model:
        return self._model

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Results.MODEL: self._model})
        return d
