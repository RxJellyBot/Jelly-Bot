from typing import Type

from bson import ObjectId

from models import Model, AutoReplyModuleModel, AutoReplyContentModel, AutoReplyModuleTagModel
from mongodb.factory.results import ModelResult, AutoReplyModuleAddResult, AutoReplyModuleTagGetResult
from tests.base import TestOnModelResult

__all__ = ["TestAutoReplyModuleAddResult", "TestAutoReplyModuleTagGetResult"]


class TestAutoReplyModuleAddResult(TestOnModelResult.TestClass):
    CHANNEL_OID = ObjectId()
    CREATOR_OID = ObjectId()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return AutoReplyModuleAddResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return AutoReplyModuleModel(
            Keyword=AutoReplyContentModel(Content="A"),
            Responses=[AutoReplyContentModel(Content="B")],
            ChannelId=TestAutoReplyModuleAddResult.CHANNEL_OID,
            CreatorOid=TestAutoReplyModuleAddResult.CREATOR_OID
        )


class TestAutoReplyModuleTagGetResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return AutoReplyModuleTagGetResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return AutoReplyModuleTagModel(Name="A")
