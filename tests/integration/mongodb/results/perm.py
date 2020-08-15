from typing import Type

from bson import ObjectId

from models import Model, ChannelProfileModel
from mongodb.factory.results import ModelResult, GetPermissionProfileResult, CreateProfileResult
from tests.base import TestOnModelResult

__all__ = ["TestGetPermissionProfileResult", "TestCreateProfileResult"]


class TestGetPermissionProfileResult(TestOnModelResult.TestClass):
    CHANNEL_OID = ObjectId()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return GetPermissionProfileResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ChannelProfileModel(ChannelOid=TestGetPermissionProfileResult.CHANNEL_OID)


class TestCreateProfileResult(TestOnModelResult.TestClass):
    CHANNEL_OID = ObjectId()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return CreateProfileResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return ChannelProfileModel(ChannelOid=TestCreateProfileResult.CHANNEL_OID)
