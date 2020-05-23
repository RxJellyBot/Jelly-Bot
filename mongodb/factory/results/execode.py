from dataclasses import dataclass
from datetime import datetime
from typing import Set, Optional

from JellyBot.api.static import result
from flags import ExecodeCompletionOutcome
from models import Model

from ._base import BaseResult, ModelResult


@dataclass
class EnqueueExecodeResult(BaseResult):
    execode: str
    expiry: datetime

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.ExecodeResponse.EXECODE: self.execode,
                    result.ExecodeResponse.EXPIRY: self.expiry})
        return d


@dataclass
class GetExecodeEntryResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[Model] = None


@dataclass
class CompleteExecodeResult(ModelResult):
    lacking_keys: Set[str]
    completion_outcome: ExecodeCompletionOutcome

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.ExecodeResponse.LACKING_KEYS: self.lacking_keys,
                    result.ExecodeResponse.COMPLETION_OUTCOME: self.completion_outcome})
        return d
