from datetime import datetime
from typing import Type

from models import Model, APIStatisticModel
from mongodb.factory.results import ModelResult, RecordAPIStatisticsResult
from tests.base import TestOnModelResult

__all__ = ["TestRecordAPIStatisticsResult"]


class TestRecordAPIStatisticsResult(TestOnModelResult.TestClass):
    TS = datetime.now()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return RecordAPIStatisticsResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return APIStatisticModel(
            Timestamp=TestRecordAPIStatisticsResult.TS, PathInfo="/a", PathInfoFull="/a/b")
