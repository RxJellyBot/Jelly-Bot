from dataclasses import dataclass
from typing import Optional

from JellyBot.api.static import result
from models import AutoReplyContentModel

from ._base import ModelResult
from ._outcome import WriteOutcome, GetOutcome


@dataclass
class AutoReplyContentAddResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: WriteOutcome
        :type model: Optional[AutoReplyContentModel]
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


@dataclass
class AutoReplyContentGetResult(ModelResult):
    def __init__(self, outcome, model, exception=None, on_add_result=None):
        """
        :type outcome: GetOutcome
        :type model: Optional[AutoReplyContentModel]
        :type exception: Optional[Exception]
        :type on_add_result: Optional[AutoReplyContentAddResult]
        """
        super().__init__(outcome, model, exception)
        self._on_add_result = on_add_result

    @property
    def on_add_result(self) -> Optional[AutoReplyContentAddResult]:
        return self._on_add_result

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.AutoReplyResponse.ADD_RESULT: self._on_add_result})
        return d


@dataclass
class AutoReplyModuleAddResult(ModelResult):
    def __init__(self, overall_outcome, model, exception=None):
        """
        :type overall_outcome: WriteOutcome
        :type model: Optional[AutoReplyModuleModel]
        :type exception: Optional[Exception]
        """
        super().__init__(overall_outcome, model, exception)


@dataclass
class AutoReplyModuleTagGetResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: GetOutcome
        :type model: AutoReplyModuleTagModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)
