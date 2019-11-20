from dataclasses import dataclass
from datetime import datetime

from JellyBot.api.static import result
from flags import ExecodeCompletionOutcome
from models import ExecodeEntryModel

from ._base import BaseResult, ModelResult
from ._outcome import WriteOutcome, OperationOutcome, GetOutcome


# noinspection DuplicatedCode
@dataclass
class EnqueueExecodeResult(BaseResult):
    def __init__(self, outcome, execode, expiry, exception=None):
        """
        :type outcome: WriteOutcome
        :type execode: str
        :type expiry: datetime
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, exception)
        self._execode = execode
        self._expiry = expiry

    @property
    def execode(self) -> str:
        return self._execode

    @property
    def expiry(self) -> datetime:
        return self._expiry

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.ExecodeResponse.EXECODE: self._execode,
                    result.ExecodeResponse.EXPIRY: self._expiry})
        return d


@dataclass
class GetExecodeEntryResult(ModelResult):
    def __init__(self, outcome, action_model):
        """
        :type outcome: GetOutcome
        :type action_model: ExecodeEntryModel
        """
        super().__init__(outcome, action_model, None)


# noinspection DuplicatedCode
@dataclass
class CompleteExecodeResult(ModelResult):
    def __init__(self, outcome, completion_outcome, action_model, lacking_keys, exception=None):
        """
        :type outcome: OperationOutcome
        :type completion_outcome: ExecodeCompletionOutcome
        :type action_model: ExecodeEntryModel
        :type lacking_keys: set
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, action_model, exception)
        self._completion_outcome = completion_outcome
        self._lacking_keys = lacking_keys

    @property
    def completion_outcome(self) -> ExecodeCompletionOutcome:
        return self._completion_outcome

    @property
    def lacking_keys(self) -> set:
        return self._lacking_keys

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.ExecodeResponse.LACKING_KEYS: self._lacking_keys,
                    result.ExecodeResponse.COMPLETION_OUTCOME: self._completion_outcome})
        return d
