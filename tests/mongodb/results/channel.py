from typing import Type

from flags import Platform
from models import Model, ChannelModel, ChannelCollectionModel
from mongodb.factory.results import (
    ModelResult, ChannelRegistrationResult, ChannelGetResult,
    ChannelChangeNameResult, ChannelCollectionRegistrationResult
)
from tests.base import TestOnModelResult

__all__ = ["TestChannelRegistrationResult", "TestChannelGetResult",
           "TestChannelChangeNameResult", "TestChannelCollectionRegistrationResult"]


class TestChannelRegistrationResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return ChannelRegistrationResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ChannelModel(
            Platform=Platform.LINE,
            Token="A12345697890"
        )


class TestChannelGetResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return ChannelGetResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ChannelModel(
            Platform=Platform.LINE,
            Token="A12345697890"
        )


class TestChannelChangeNameResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return ChannelChangeNameResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ChannelModel(
            Platform=Platform.LINE,
            Token="A12345697890"
        )


class TestChannelCollectionRegistrationResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return ChannelCollectionRegistrationResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ChannelCollectionModel(
            DefaultName="Name",
            Platform=Platform.LINE,
            Token="A12345697890"
        )
