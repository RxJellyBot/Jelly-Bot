from typing import Type, Tuple, Any

from bson import ObjectId

from JellyBot.api.static import result
from flags import Platform
from models import Model, APIUserModel, OnPlatformUserModel, RootUserModel
from mongodb.factory.results import (
    ModelResult, OnSiteUserRegistrationResult, OnPlatformUserRegistrationResult, GetRootUserDataResult,
    RootUserRegistrationResult, RootUserUpdateResult, GetOutcome, WriteOutcome
)
from tests.base import TestOnModelResult

__all__ = ["TestOnSiteUserRegistrationResult", "TestOnPlatformUserRegistrationResult",
           "TestGetRootUserDataResult", "TestRootUserRegistrationResult", "TestRootUserUpdateResult"]


class TestOnSiteUserRegistrationResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return OnSiteUserRegistrationResult

    @classmethod
    def result_args_no_error(cls) -> Tuple[Any, ...]:
        return "ABCD",

    @classmethod
    def result_args_has_error(cls) -> Tuple[Any, ...]:
        return "EFGH",

    @classmethod
    def default_serialized(cls):
        d = super().default_serialized()
        d.update({result.UserManagementResponse.TOKEN: "ABCD"})
        return d

    @classmethod
    def default_serialized_error(cls):
        d = super().default_serialized_error()
        d.update({result.UserManagementResponse.TOKEN: "EFGH"})
        return d

    @classmethod
    def get_constructed_model(cls) -> Model:
        return APIUserModel(Email="a@b.com", GoogleUid="123456789", Token="A" * APIUserModel.API_TOKEN_LENGTH)


class TestOnPlatformUserRegistrationResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return OnPlatformUserRegistrationResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return OnPlatformUserModel(Token="ABC", Platform=Platform.LINE)


class TestGetRootUserDataResult(TestOnModelResult.TestClass):
    API_OID = ObjectId()

    @classmethod
    def get_result_class(cls) -> Type[ModelResult]:
        return GetRootUserDataResult

    @classmethod
    def get_constructed_model(cls) -> RootUserModel:
        return RootUserModel(ApiOid=TestGetRootUserDataResult.API_OID)

    def test_get_extra(self):
        mdl_api = APIUserModel(Email="a@b.com", GoogleUid="123456789", Token="A" * APIUserModel.API_TOKEN_LENGTH)
        mdl_onplat = [OnPlatformUserModel(Token="ABC", Platform=Platform.LINE)]

        r = GetRootUserDataResult(GetOutcome.O_ADDED, None, self.get_constructed_model(), mdl_api, mdl_onplat)

        self.assertEqual(r.model_api, mdl_api)
        self.assertEqual(r.model_onplat_list, mdl_onplat)


class TestRootUserRegistrationResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls):
        return RootUserRegistrationResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return RootUserModel(ApiOid=TestGetRootUserDataResult.API_OID)

    @classmethod
    def result_args_no_error(cls) -> Tuple[Any, ...]:
        return \
            WriteOutcome.O_INSERTED, \
            OnPlatformUserRegistrationResult(
                WriteOutcome.O_MISC, None, OnPlatformUserModel(Token="ABC", Platform=Platform.LINE)), \
            "ApiOid"

    @classmethod
    def result_args_has_error(cls) -> Tuple[Any, ...]:
        return WriteOutcome.X_NOT_EXECUTED, None, ""

    @classmethod
    def default_serialized(cls):
        d = super().default_serialized()
        d.update({result.UserManagementResponse.CONN_OUTCOME: WriteOutcome.O_INSERTED,
                  result.UserManagementResponse.REG_RESULT: OnPlatformUserRegistrationResult(
                      WriteOutcome.O_MISC,
                      None,
                      OnPlatformUserModel(Token="ABC", Platform=Platform.LINE)).serialize(),
                  result.UserManagementResponse.HINT: "ApiOid"})
        return d

    @classmethod
    def default_serialized_error(cls):
        d = super().default_serialized_error()
        d.update({result.UserManagementResponse.CONN_OUTCOME: WriteOutcome.X_NOT_EXECUTED,
                  result.UserManagementResponse.REG_RESULT: None,
                  result.UserManagementResponse.HINT: ""})
        return d


class TestRootUserUpdateResult(TestOnModelResult.TestClass):
    @classmethod
    def get_result_class(cls):
        return RootUserUpdateResult

    @classmethod
    def get_constructed_model(cls) -> Model:
        return RootUserModel(ApiOid=TestGetRootUserDataResult.API_OID)
