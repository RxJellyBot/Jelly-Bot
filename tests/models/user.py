from typing import Dict, Tuple, Any, Type, List

from bson import ObjectId
from django.test import TestCase

from extutils import exec_timing_result
from extutils.locales import default_locale, default_language, LocaleInfo
from flags import ModelValidityCheckResult, Platform
from models import RootUserConfigModel, Model, RootUserModel, APIUserModel, OnPlatformUserModel, ChannelModel
from models.exceptions import InvalidModelError, ModelConstructionError, InvalidModelFieldError

from ._test_base import TestModel

__all__ = ["TestRootUserConfigModel", "TestRootUserModelFillApi", "TestRootUserModelFillOnPlat",
           "TestRootUserModelValidity", "TestAPIUserModel", "TestOnPlatformUserModel"]


class TestRootUserConfigModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return RootUserConfigModel

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("l", "Locale"): (default_locale.pytz_code, "US/Central"),
            ("lg", "Language"): (default_language.code, "en_US"),
            ("n", "Name"): ("", "ABCD")
        }

    def test_get_tzinfo(self):
        mdl = self.get_constructed_model(manual_default=False)
        self.assertEqual(LocaleInfo.get_tzinfo(default_locale.pytz_code), mdl.tzinfo)
        mdl = self.get_constructed_model(manual_default=True)
        self.assertEqual(LocaleInfo.get_tzinfo("US/Central"), mdl.tzinfo)


class TestRootUserModelFillApi(TestModel.TestClass):
    ONPLAT = ObjectId()
    API = ObjectId()
    CONFIG = RootUserConfigModel()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return RootUserModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("api", "ApiOid"): TestRootUserModelFillApi.API
        }

    @classmethod
    def get_required_invalid(cls) -> List[Tuple[Dict[Tuple[str, str], Any], Type[ModelConstructionError]]]:
        return [
            (
                {},
                InvalidModelError
            ),
        ]

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("c", "Config"): (TestRootUserModelFillApi.CONFIG, RootUserConfigModel(Locale="US/Central"))
        }

    @classmethod
    def get_optional(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("op", "OnPlatOids"): [TestRootUserModelFillApi.ONPLAT]
        }


class TestRootUserModelFillOnPlat(TestModel.TestClass):
    ONPLAT = ObjectId()
    API = ObjectId()
    CONFIG = RootUserConfigModel()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return RootUserModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("op", "OnPlatOids"): [TestRootUserModelFillApi.ONPLAT]
        }

    @classmethod
    def get_required_invalid(cls) -> List[Tuple[Dict[Tuple[str, str], Any], Type[ModelConstructionError]]]:
        return [
            (
                {},
                InvalidModelError
            ),
        ]

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("c", "Config"): (TestRootUserModelFillApi.CONFIG, RootUserConfigModel(Locale="US/Central"))
        }

    @classmethod
    def get_optional(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("api", "ApiOid"): TestRootUserModelFillApi.API
        }


class TestRootUserModelValidity(TestCase):
    def test_all_none(self):
        with self.assertRaises(InvalidModelError) as e:
            RootUserModel()

        self.assertEqual(e.exception.reason, ModelValidityCheckResult.X_RTU_ALL_NONE)

    def test_api_only(self):
        mdl = RootUserModel(ApiOid=ObjectId())
        self.assertTrue(mdl.has_api_data)
        self.assertFalse(mdl.has_onplat_data)

    def test_onplat_only(self):
        mdl = RootUserModel(OnPlatOids=[ObjectId()])
        self.assertFalse(mdl.has_api_data)
        self.assertTrue(mdl.has_onplat_data)

    def test_api_onplat(self):
        mdl = RootUserModel(OnPlatOids=[ObjectId()], ApiOid=ObjectId())
        self.assertTrue(mdl.has_api_data)
        self.assertTrue(mdl.has_onplat_data)


class TestAPIUserModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return APIUserModel

    @classmethod
    def get_required_invalid(cls) -> List[Tuple[Dict[Tuple[str, str], Any], Type[ModelConstructionError]]]:
        return [
            (
                {
                    ("e", "Email"): "agmail.com",
                    ("goo_id", "GoogleUid"): "10101010101010101",
                    ("t", "Token"): "1" * APIUserModel.API_TOKEN_LENGTH
                },
                InvalidModelFieldError
            ),
            (
                {
                    ("e", "Email"): "a@gmail.com",
                    ("goo_id", "GoogleUid"): "10101010101010101",
                    ("t", "Token"): "1" * (APIUserModel.API_TOKEN_LENGTH - 1)
                },
                InvalidModelFieldError
            ),
            (
                {
                    ("e", "Email"): "a@gmail.com",
                    ("goo_id", "GoogleUid"): "",
                    ("t", "Token"): "1" * (APIUserModel.API_TOKEN_LENGTH - 1)
                },
                InvalidModelFieldError
            )
        ]

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("e", "Email"): "a@gmail.com",
            ("goo_id", "GoogleUid"): "10101010101010101",
            ("t", "Token"): "1" * APIUserModel.API_TOKEN_LENGTH
        }


class TestOnPlatformUserModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return OnPlatformUserModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("t", "Token"): "U1234567890",
            ("p", "Platform"): Platform.LINE
        }

    def test_get_name(self):
        cmdl = ChannelModel(Platform=Platform.LINE, Token="U1234567890")

        mdl = self.get_constructed_model()
        mdl.set_oid(ObjectId())
        self.assertIsNone(mdl.get_name(cmdl))
        self.assertEqual("U1234567890 (LINE)", mdl.get_name_str(cmdl))

        cmdl = ChannelModel(Platform=Platform.LINE, Token="Ubff224fa18b8cf010da6d6bc88da8f55")

        mdl = self.get_constructed_model(t="Ubff224fa18b8cf010da6d6bc88da8f55")
        mdl.set_oid(ObjectId())
        self.assertIsNotNone(mdl.get_name(cmdl))
        self.assertNotEqual("Ubff224fa18b8cf010da6d6bc88da8f55 (LINE)", mdl.get_name_str(cmdl))

    def test_get_name_cache(self):
        cmdl = ChannelModel(Platform=Platform.LINE, Token="Ubff224fa18b8cf010da6d6bc88da8f55")

        mdl = self.get_constructed_model(t="Ubff224fa18b8cf010da6d6bc88da8f55")
        mdl.set_oid(ObjectId())
        self.assertIsNotNone(mdl.get_name(cmdl))
        self.assertNotEqual("Ubff224fa18b8cf010da6d6bc88da8f55 (LINE)", mdl.get_name_str(cmdl))

        exec_result = exec_timing_result(mdl.get_name, cmdl)
        self.assertLess(exec_result.execution_ms, 10)
        self.assertIsNotNone(exec_result.return_)
