from dataclasses import dataclass
from datetime import datetime
from typing import Set, Optional

from JellyBot.api.static import result
from flags import ExecodeCompletionOutcome
from models import ExecodeEntryModel

from ._base import ModelResult


@dataclass
class EnqueueExecodeResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[ExecodeEntryModel] = None
    execode: Optional[str] = None
    expiry: Optional[datetime] = None

    def serialize(self) -> dict:
        d = super().serialize()

        d.update(**{result.ExecodeResponse.EXECODE: self.execode,
                    result.ExecodeResponse.EXPIRY: self.expiry})
        return d


@dataclass
class GetExecodeEntryResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[ExecodeEntryModel] = None


@dataclass
class CompleteExecodeResult(ModelResult):
    model: Optional[ExecodeEntryModel]
    missing_keys: Set[str]
    completion_outcome: ExecodeCompletionOutcome

    @property
    def success(self) -> bool:
        return super().success and not self.missing_keys

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.ExecodeResponse.MISSING_ARGS: self.missing_keys,
                    result.ExecodeResponse.COMPLETION_OUTCOME: self.completion_outcome})
        return d
