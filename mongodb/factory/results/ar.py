from dataclasses import dataclass
from typing import Optional

from JellyBotAPI.api.static import result
from models import AutoReplyContentModel, AutoReplyConnectionModel

from ._base import ModelResult
from ._outcome import InsertOutcome, GetOutcome


@dataclass
class AutoReplyContentAddResult(ModelResult):
    def __init__(self, outcome, model, exception=None):
        """
        :type outcome: InsertOutcome
        :type model: AutoReplyContentModel
        :type exception: Optional[Exception]
        """
        super().__init__(outcome, model, exception)


@dataclass
class AutoReplyContentGetResult(ModelResult):
    def __init__(self, outcome, model, exception=None, on_add_result=None):
        """
        :type outcome: GetOutcome
        :type model: AutoReplyContentModel
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
        d.update(**{result.Results.ADD_RESULT: self._on_add_result})
        return d


@dataclass
class AutoReplyConnectionAddResult(ModelResult):
    def __init__(self, overall_outcome, insert_conn_outcome, model, exception=None):
        """
        :type overall_outcome: InsertOutcome
        :type insert_conn_outcome: InsertOutcome
        :type model: AutoReplyConnectionModel
        :type exception: Optional[Exception]
        """
        super().__init__(overall_outcome, model, exception)
        self._insert_conn_outcome = insert_conn_outcome

    @property
    def insert_conn_outcome(self) -> InsertOutcome:
        return self._insert_conn_outcome

    @property
    def success(self) -> bool:
        return InsertOutcome.is_success(self._outcome)

    def serialize(self) -> dict:
        d = super().serialize()
        d.update(**{result.Results.INSERT_CONN_OUTCOME: self._insert_conn_outcome})
        return d
