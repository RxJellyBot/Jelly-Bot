from datetime import datetime
from typing import Type

from models import Model, ExtraContentModel
from mongodb.factory.results import ModelResult, RecordExtraContentResult
from tests.base import TestOnModelResult

__all__ = ["TestRecordExtraContentResult"]


class TestRecordExtraContentResult(TestOnModelResult.TestClass):
    TS = datetime.utcnow()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return RecordExtraContentResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ExtraContentModel(Content="AAAAA", Timestamp=TestRecordExtraContentResult.TS)
