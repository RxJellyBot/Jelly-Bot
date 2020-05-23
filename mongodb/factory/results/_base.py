from abc import ABC
from dataclasses import dataclass
from typing import Optional

from JellyBot.api.static import result
from models import Model

from ._outcome import BaseOutcome


@dataclass
class BaseResult(ABC):
    outcome: BaseOutcome
    exception: Optional[Exception]

    def serialize(self) -> dict:
        return {result.Results.EXCEPTION: repr(self.exception),
                result.Results.OUTCOME: self.outcome.code}

    @property
    def success(self) -> bool:
        return self.outcome.is_success


@dataclass
class ModelResult(BaseResult, ABC):
    model: Optional[Model]

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Results.MODEL: self.model})
        return d
