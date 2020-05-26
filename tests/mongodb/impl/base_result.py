from dataclasses import dataclass
from typing import Type

from models import Model
from mongodb.factory.results import BaseResult, ModelResult
from tests.base import TestOnModelResult, TestOnBaseResult

__all__ = ["TestBaseResult", "TestModelResult"]


class TestBaseResult(TestOnBaseResult.TestClass):
    @dataclass
    class Result(BaseResult):
        pass

    @classmethod
    def get_result_class(cls) -> Type[BaseResult]:
        return TestBaseResult.Result


class TestModelResult(TestOnModelResult.TestClass):
    @dataclass
    class Result(ModelResult):
        pass

    class TestModel(Model):
        pass

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return TestModelResult.Result

    @classmethod
    def get_constructed_model(cls) -> Model:
        return TestModelResult.TestModel()
