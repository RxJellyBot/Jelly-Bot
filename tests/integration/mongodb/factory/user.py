from bson import ObjectId

from extutils.gidentity import GoogleIdentityUserData
from extutils.locales import DEFAULT_LOCALE, USA_CENT
from flags import Platform
from models import (
    OID_KEY, APIUserModel, OnPlatformUserModel, RootUserModel, RootUserConfigModel, ChannelModel, ChannelConfigModel
)
from mongodb.factory import RootUserManager
from mongodb.factory.results import WriteOutcome, GetOutcome, UpdateOutcome, OperationOutcome
from mongodb.factory.user import APIUserManager, OnPlatformIdentityManager
from tests.base import TestModelMixin

__all__ = ("TestAPIUserManager", "TestOnPlatformIdentityManager", "TestRootUserManager",)


class TestAPIUserManager(TestModelMixin):
    GOO_IDENTITY = GoogleIdentityUserData("FakeAUD", "FakeISS", "FakeUID", "Fake2@email.com", skip_check=True)

    @staticmethod
    def obj_to_clear():
        return [APIUserManager]

    def test_register(self):
        result = APIUserManager.register(self.GOO_IDENTITY)

        self.assertTrue(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertModelEqual(
            result.model,
            APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID", Token=result.model.token)
        )
        self.assertTrue(result.success)
        self.assertEqual(result.token, result.model.token)

    def test_register_already_exists(self):
        mdl = APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        APIUserManager.insert_one(mdl)

        result = APIUserManager.register(self.GOO_IDENTITY)

        self.assertTrue(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNotNone(result.exception)
        self.assertModelEqual(result.model, mdl)
        self.assertTrue(result.success)
        self.assertEqual(result.token, "Toke" * 8)

    def test_get_user_data_id_data(self):
        mdl_exists = APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        APIUserManager.insert_one(mdl_exists)

        mdl = APIUserManager.get_user_data_id_data(self.GOO_IDENTITY)

        self.assertModelEqual(mdl, mdl_exists)

    def test_get_user_data_id_data_missed(self):
        APIUserManager.insert_one(APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID22", Token="Toke" * 8))

        self.assertIsNone(APIUserManager.get_user_data_id_data(self.GOO_IDENTITY))

    def test_get_user_data_id_data_no_data(self):
        self.assertIsNone(APIUserManager.get_user_data_id_data(self.GOO_IDENTITY))

    def test_get_user_data_token(self):
        mdl_exists = APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        APIUserManager.insert_one(mdl_exists)

        mdl = APIUserManager.get_user_data_token("Toke" * 8)

        self.assertEqual(mdl, mdl_exists)

    def test_get_user_data_token_missed(self):
        APIUserManager.insert_one(APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID22", Token="Toke" * 8))

        self.assertIsNone(APIUserManager.get_user_data_token("Toka" * 8))

    def test_get_user_data_token_no_data(self):
        self.assertIsNone(APIUserManager.get_user_data_token("Toke" * 8))

    def test_get_user_data_google_id(self):
        mdl_exists = APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        APIUserManager.insert_one(mdl_exists)

        mdl = APIUserManager.get_user_data_google_id("FakeUID")

        self.assertEqual(mdl, mdl_exists)

    def test_get_user_data_google_id_missed(self):
        APIUserManager.insert_one(APIUserModel(Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8))

        self.assertIsNone(APIUserManager.get_user_data_google_id("FakeUIDEEE"))

    def test_get_user_data_google_id_no_data(self):
        self.assertIsNone(APIUserManager.get_user_data_google_id("FakeUID"))


class TestOnPlatformIdentityManager(TestModelMixin):
    @staticmethod
    def obj_to_clear():
        return [OnPlatformIdentityManager]

    def test_register(self):
        result = OnPlatformIdentityManager.register(Platform.LINE, "U123456")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, OnPlatformUserModel(Token="U123456", Platform=Platform.LINE))

    def test_register_already_exists(self):
        mdl = OnPlatformUserModel(Token="U123456", Platform=Platform.LINE)
        OnPlatformIdentityManager.insert_one(mdl)

        result = OnPlatformIdentityManager.register(Platform.LINE, "U123456")

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertIsNotNone(result.exception)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl)

    def test_get_onplat(self):
        mdl_exists = OnPlatformUserModel(Token="U123456", Platform=Platform.LINE)
        OnPlatformIdentityManager.insert_one(mdl_exists)

        mdl = OnPlatformIdentityManager.get_onplat(Platform.LINE, "U123456")

        self.assertModelEqual(mdl, mdl_exists)

    def test_get_onplat_missed(self):
        mdl_exists = OnPlatformUserModel(Token="U123456", Platform=Platform.LINE)
        OnPlatformIdentityManager.insert_one(mdl_exists)

        self.assertIsNone(OnPlatformIdentityManager.get_onplat(Platform.LINE, "U12345A"))

    def test_get_onplat_no_data(self):
        self.assertIsNone(OnPlatformIdentityManager.get_onplat(Platform.LINE, "U123456"))

    def test_get_onplat_by_oid(self):
        mdl_exists = OnPlatformUserModel(Token="U123456", Platform=Platform.LINE)
        OnPlatformIdentityManager.insert_one(mdl_exists)

        mdl = OnPlatformIdentityManager.get_onplat_by_oid(mdl_exists.id)

        self.assertModelEqual(mdl, mdl_exists)

    def test_get_onplat_by_oid_missed(self):
        mdl_exists = OnPlatformUserModel(Token="U123456", Platform=Platform.LINE)
        OnPlatformIdentityManager.insert_one(mdl_exists)

        self.assertIsNone(OnPlatformIdentityManager.get_onplat_by_oid(ObjectId()))

    def test_get_onplat_by_oid_no_data(self):
        self.assertIsNone(OnPlatformIdentityManager.get_onplat_by_oid(ObjectId()))


class TestRootUserManager(TestModelMixin):
    ROOT_OID = ObjectId()
    ROOT_OID_2 = ObjectId()
    ROOT_OID_3 = ObjectId()
    ONPLAT_OID = ObjectId()
    ONPLAT_OID_2 = ObjectId()
    ONPLAT_OID_3 = ObjectId()
    ONPLAT_OID_4 = ObjectId()
    API_OID = ObjectId()
    API_OID_2 = ObjectId()

    GOO_IDENTITY = GoogleIdentityUserData("FakeAUD", "FakeISS", "FakeUID", "Fake@email.com", skip_check=True)
    GOO_IDENTITY_2 = GoogleIdentityUserData("FakeAUD2", "FakeISS2", "FakeUID2", "Fake2@email.com", skip_check=True)

    DISCORD_TOKEN = 360461600542425108  # Actually exists

    LINE_TOKEN = "U4c94d18c660743c963fd3a08a025b8b3"  # Actually exists
    LINE_TOKEN_2 = "U4c94d18c660743c963fd3a08a025b8b4"  # Dummy
    LINE_NAME = "RaenonX"  # Actual name
    LINE_CHANNEL_MODEL = ChannelModel(
        Id=ObjectId("5dd1bd8290ff56e291b72e65"), Platform=Platform.LINE, Token="C2525832a417beda4e9cde5c335620736",
        Config=ChannelConfigModel(DefaultProfileOid=ObjectId())
    )  # Actually exists

    @staticmethod
    def obj_to_clear():
        return [RootUserManager]

    def test_register_onplat(self):
        result = RootUserManager.register_onplat(Platform.LINE, "U123456")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertEqual(result.conn_outcome, WriteOutcome.O_INSERTED)
        self.assertModelEqual(
            result.idt_reg_result.model,
            OnPlatformUserModel(Token="U123456", Platform=Platform.LINE)
        )
        self.assertModelEqual(
            result.model,
            RootUserModel(OnPlatOids=[result.idt_reg_result.model.id], Config=RootUserConfigModel.generate_default())
        )

    def test_register_onplat_exists(self):
        RootUserManager.insert_one(RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                                                 Config=RootUserConfigModel.generate_default()))
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Token="U123456", Platform=Platform.LINE)
        )

        result = RootUserManager.register_onplat(Platform.LINE, "U123456")

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertEqual(result.conn_outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertModelEqual(
            result.idt_reg_result.model,
            OnPlatformUserModel(Token="U123456", Platform=Platform.LINE)
        )
        self.assertModelEqual(
            result.model,
            RootUserModel(Id=self.ROOT_OID, OnPlatOids=[result.idt_reg_result.model.id],
                          Config=RootUserConfigModel.generate_default())
        )

    def test_register_google(self):
        result = RootUserManager.register_google(self.GOO_IDENTITY)

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertEqual(result.conn_outcome, WriteOutcome.O_INSERTED)
        self.assertModelEqual(
            result.idt_reg_result.model,
            APIUserModel(Email="Fake@email.com", GoogleUid="FakeUID", Token=result.idt_reg_result.token)
        )
        self.assertModelEqual(
            result.model,
            RootUserModel(ApiOid=result.idt_reg_result.model.id, Config=RootUserConfigModel.generate_default())
        )

    def test_register_google_exists(self):
        RootUserManager.insert_one(RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID,
                                                 Config=RootUserConfigModel.generate_default()))
        APIUserManager.insert_one(APIUserModel(Id=self.API_OID, Email="Fake@email.com",
                                               GoogleUid="FakeUID", Token="Toke" * 8))

        result = RootUserManager.register_google(self.GOO_IDENTITY)

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertEqual(result.conn_outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertModelEqual(
            result.idt_reg_result.model,
            APIUserModel(Id=self.API_OID, Email="Fake@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        )
        self.assertEqual(
            result.model,
            RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default())
        )

    def test_get_root_data_oid(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)

        ret = RootUserManager.get_root_data_oid(self.ROOT_OID)
        self.assertEqual(mdl, ret)

    def test_get_root_data_oid_str_oid(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)

        ret = RootUserManager.get_root_data_oid(str(self.ROOT_OID))
        self.assertEqual(mdl, ret)

    def test_get_root_data_oid_missed(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)

        ret = RootUserManager.get_root_data_oid(ObjectId())
        self.assertIsNone(ret)

    def test_get_root_data_oid_no_data(self):
        ret = RootUserManager.get_root_data_oid(self.ROOT_OID)
        self.assertIsNone(ret)

    def test_get_root_data_uname_name_defined(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID,
                            Config=RootUserConfigModel.generate_default(Name="UserName"))
        RootUserManager.insert_one(mdl)

        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID),
            (self.ROOT_OID, "UserName")
        )

    def test_get_root_data_uname_no_onplat(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)

        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID),
            (self.ROOT_OID, f"UID - {self.ROOT_OID}")
        )
        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID, on_not_found="N/A"),
            (self.ROOT_OID, "N/A")
        )

    def test_get_root_data_uname_has_onplat_no_channel_data_line(self):
        mdl = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                            Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        )

        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID),
            (self.ROOT_OID, self.LINE_NAME)
        )
        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID, on_not_found="N/A"),
            (self.ROOT_OID, self.LINE_NAME)
        )

    def test_get_root_data_uname_has_onplat_with_channel_data(self):
        mdl = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                            Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        )

        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID, self.LINE_CHANNEL_MODEL),
            (self.ROOT_OID, self.LINE_NAME)
        )
        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID, self.LINE_CHANNEL_MODEL, on_not_found="N/A"),
            (self.ROOT_OID, self.LINE_NAME)
        )

    def test_get_root_data_uname_has_onplat_name_unavailable(self):
        mdl = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                            Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token="U123456")
        )

        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID, self.LINE_CHANNEL_MODEL),
            (self.ROOT_OID, "U123456 (LINE)")
        )
        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID, self.LINE_CHANNEL_MODEL, on_not_found="N/A"),
            (self.ROOT_OID, "N/A")
        )

    def test_get_root_data_uname_has_both(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, OnPlatOids=[self.ONPLAT_OID],
                            Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl)
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        )

        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID),
            (self.ROOT_OID, "RaenonX")
        )
        self.assertEqual(
            RootUserManager.get_root_data_uname(self.ROOT_OID, on_not_found="N/A"),
            (self.ROOT_OID, "RaenonX")
        )

    def test_get_root_data_uname_str_oid(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID,
                            Config=RootUserConfigModel.generate_default(Name="UserName"))
        RootUserManager.insert_one(mdl)

        self.assertEqual(
            RootUserManager.get_root_data_uname(str(self.ROOT_OID)),
            (self.ROOT_OID, "UserName")
        )

    def test_get_root_data_uname_missed(self):
        mdl = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID,
                            Config=RootUserConfigModel.generate_default(Name="UserName"))
        RootUserManager.insert_one(mdl)

        self.assertIsNone(RootUserManager.get_root_data_uname(ObjectId()))

    def test_get_root_data_uname_no_data(self):
        self.assertIsNone(RootUserManager.get_root_data_uname(self.ROOT_OID))

    def test_get_root_data_api_token_skip_onplat_no_onplat(self):
        mdl_api = APIUserModel(Id=self.API_OID, Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        mdl_root = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_one(mdl_api)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_api_token("Toke" * 8)
        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl_root)
        self.assertEqual(result.model_api, mdl_api)
        self.assertEqual(result.model_onplat_list, [])

    def test_get_root_data_api_token_skip_onplat_has_onplat(self):
        mdl_api = APIUserModel(Id=self.API_OID, Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_root = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, OnPlatOids=[self.ONPLAT_OID],
                                 Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_one(mdl_api)
        OnPlatformIdentityManager.insert_one(mdl_onplat)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_api_token("Toke" * 8)
        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl_root)
        self.assertEqual(result.model_api, mdl_api)
        self.assertEqual(result.model_onplat_list, [])

    def test_get_root_data_api_token_dont_skip_onplat_no_onplat(self):
        mdl_api = APIUserModel(Id=self.API_OID, Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        mdl_root = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_one(mdl_api)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_api_token("Toke" * 8, skip_on_plat=False)
        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl_root)
        self.assertEqual(result.model_api, mdl_api)
        self.assertEqual(result.model_onplat_list, [])

    def test_get_root_data_api_token_dont_skip_onplat_has_onplat(self):
        mdl_api = APIUserModel(Id=self.API_OID, Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_root = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, OnPlatOids=[self.ONPLAT_OID],
                                 Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_one(mdl_api)
        OnPlatformIdentityManager.insert_one(mdl_onplat)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_api_token("Toke" * 8, skip_on_plat=False)
        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl_root)
        self.assertEqual(result.model_api, mdl_api)
        self.assertEqual(result.model_onplat_list, [mdl_onplat])

    def test_get_root_data_api_token_missed(self):
        mdl_api = APIUserModel(Id=self.API_OID, Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_root = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID, OnPlatOids=[self.ONPLAT_OID],
                                 Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_one(mdl_api)
        OnPlatformIdentityManager.insert_one(mdl_onplat)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_api_token("Toka" * 8)
        self.assertEqual(result.outcome, GetOutcome.X_NOT_FOUND_FIRST_QUERY)
        self.assertFalse(result.success)

    def test_get_root_data_api_token_no_root(self):
        mdl_api = APIUserModel(Id=self.API_OID, Email="Fake2@email.com", GoogleUid="FakeUID", Token="Toke" * 8)
        APIUserManager.insert_one(mdl_api)

        result = RootUserManager.get_root_data_api_token("Toke" * 8)
        self.assertEqual(result.outcome, GetOutcome.X_NOT_FOUND_SECOND_QUERY)
        self.assertFalse(result.success)

    def test_get_root_data_api_token_no_data(self):
        result = RootUserManager.get_root_data_api_token("Toke" * 8)
        self.assertEqual(result.outcome, GetOutcome.X_NOT_FOUND_FIRST_QUERY)
        self.assertFalse(result.success)

    def test_get_root_data_onplat(self):
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_root = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                                 Config=RootUserConfigModel.generate_default())
        OnPlatformIdentityManager.insert_one(mdl_onplat)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_onplat(Platform.LINE, self.LINE_TOKEN, auto_register=False)
        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl_root)
        self.assertIsNone(result.model_api)
        self.assertIsNone(result.model_onplat_list)

    def test_get_root_data_onplat_missed(self):
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_root = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                                 Config=RootUserConfigModel.generate_default())
        OnPlatformIdentityManager.insert_one(mdl_onplat)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_onplat(Platform.LINE, self.LINE_TOKEN + "789", auto_register=False)
        self.assertEqual(result.outcome, GetOutcome.X_NOT_FOUND_ABORTED_INSERT)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)
        self.assertIsNone(result.model_api)
        self.assertIsNone(result.model_onplat_list)

    def test_get_root_data_onplat_auto_register(self):
        result = RootUserManager.get_root_data_onplat(Platform.LINE, self.LINE_TOKEN)
        self.assertEqual(result.outcome, GetOutcome.O_ADDED)
        self.assertTrue(result.success)
        mdl_onplat = OnPlatformIdentityManager.find_one({OnPlatformUserModel.Platform.key: Platform.LINE,
                                                         OnPlatformUserModel.Token.key: self.LINE_TOKEN})
        self.assertIsNotNone(mdl_onplat)
        self.assertEqual(
            RootUserManager.count_documents({
                RootUserModel.OnPlatOids.key: mdl_onplat[OID_KEY]
            }),
            1
        )

    def test_get_root_data_onplat_auto_register_exists(self):
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_root = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                                 Config=RootUserConfigModel.generate_default())
        OnPlatformIdentityManager.insert_one(mdl_onplat)
        RootUserManager.insert_one(mdl_root)

        result = RootUserManager.get_root_data_onplat(Platform.LINE, self.LINE_TOKEN)
        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertEqual(result.model, mdl_root)
        self.assertIsNone(result.model_api)
        self.assertIsNone(result.model_onplat_list)

    def test_get_root_data_onplat_no_data(self):
        result = RootUserManager.get_root_data_onplat(Platform.LINE, self.LINE_TOKEN, auto_register=False)

        self.assertEqual(result.outcome, GetOutcome.X_NOT_FOUND_ABORTED_INSERT)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)
        self.assertIsNone(result.model_api)
        self.assertIsNone(result.model_onplat_list)

    def test_get_onplat_data(self):
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        OnPlatformIdentityManager.insert_one(mdl_onplat)

        ret = RootUserManager.get_onplat_data(Platform.LINE, self.LINE_TOKEN)
        self.assertEqual(mdl_onplat, ret)

    def test_get_onplat_data_int_plat(self):
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        OnPlatformIdentityManager.insert_one(mdl_onplat)

        ret = RootUserManager.get_onplat_data(1, self.LINE_TOKEN)
        self.assertEqual(mdl_onplat, ret)

    def test_get_onplat_data_missed(self):
        mdl_onplat = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        OnPlatformIdentityManager.insert_one(mdl_onplat)

        self.assertIsNone(RootUserManager.get_onplat_data(Platform.DISCORD, self.LINE_TOKEN))

    def test_get_onplat_data_no_data(self):
        self.assertIsNone(RootUserManager.get_onplat_data(Platform.LINE, self.LINE_TOKEN))

    def test_get_onplat_data_dict(self):
        mdl_onplat_1 = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_onplat_2 = OnPlatformUserModel(Id=self.ONPLAT_OID_2, Platform=Platform.LINE, Token=self.LINE_TOKEN_2)
        OnPlatformIdentityManager.insert_many([mdl_onplat_1, mdl_onplat_2])

        self.assertEqual(
            RootUserManager.get_onplat_data_dict(),
            {
                self.ONPLAT_OID: mdl_onplat_1,
                self.ONPLAT_OID_2: mdl_onplat_2
            }
        )

    def test_get_onplat_data_dict_no_data(self):
        self.assertEqual(RootUserManager.get_onplat_data_dict(), {})

    def test_get_onplat_to_root_dict(self):
        mdl_onplat_1 = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_onplat_2 = OnPlatformUserModel(Id=self.ONPLAT_OID_2, Platform=Platform.LINE, Token=self.LINE_TOKEN_2)
        OnPlatformIdentityManager.insert_many([mdl_onplat_1, mdl_onplat_2])
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID],
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, OnPlatOids=[self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        self.assertEqual(
            RootUserManager.get_onplat_to_root_dict(),
            {
                mdl_onplat_1.id: mdl_root_1.id,
                mdl_onplat_2.id: mdl_root_2.id
            }
        )

    def test_get_onplat_to_root_dict_multi_to_one(self):
        mdl_onplat_1 = OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        mdl_onplat_2 = OnPlatformUserModel(Id=self.ONPLAT_OID_2, Platform=Platform.LINE, Token=self.LINE_TOKEN_2)
        OnPlatformIdentityManager.insert_many([mdl_onplat_1, mdl_onplat_2])
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(
            RootUserManager.get_onplat_to_root_dict(),
            {
                mdl_onplat_1.id: mdl_root_1.id,
                mdl_onplat_2.id: mdl_root_1.id
            }
        )

    def test_get_onplat_to_root_dict_no_data(self):
        self.assertEqual(RootUserManager.get_onplat_to_root_dict(), {})

    def _get_root_to_onplat_dict_prep(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, OnPlatOids=[self.ONPLAT_OID_3],
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_3 = RootUserModel(Id=self.ROOT_OID_3, OnPlatOids=[self.ONPLAT_OID_4],
                                   Config=RootUserConfigModel.generate_default())

        RootUserManager.insert_many([mdl_root_1, mdl_root_2, mdl_root_3])

    def test_get_root_to_onplat_dict_unrestricted(self):
        self._get_root_to_onplat_dict_prep()

        self.assertEqual(
            RootUserManager.get_root_to_onplat_dict(),
            {
                self.ROOT_OID: [self.ONPLAT_OID, self.ONPLAT_OID_2],
                self.ROOT_OID_2: [self.ONPLAT_OID_3],
                self.ROOT_OID_3: [self.ONPLAT_OID_4]
            }
        )

    def test_get_root_to_onplat_dict_restricted(self):
        self._get_root_to_onplat_dict_prep()

        self.assertEqual(
            RootUserManager.get_root_to_onplat_dict([self.ROOT_OID, self.ROOT_OID_2]),
            {
                self.ROOT_OID: [self.ONPLAT_OID, self.ONPLAT_OID_2],
                self.ROOT_OID_2: [self.ONPLAT_OID_3]
            }
        )

    def test_get_root_to_onplat_dict_no_data(self):
        self.assertEqual(RootUserManager.get_root_to_onplat_dict(), {})
        self.assertEqual(RootUserManager.get_root_to_onplat_dict([self.ROOT_OID]), {})

    def test_get_root_data_api_oid(self):
        mdl_api_1 = APIUserModel(Id=self.API_OID, Email=self.GOO_IDENTITY.email,
                                 GoogleUid=self.GOO_IDENTITY.uid, Token="Toke" * 8)
        mdl_api_2 = APIUserModel(Id=self.API_OID_2, Email=self.GOO_IDENTITY_2.email,
                                 GoogleUid=self.GOO_IDENTITY_2.uid, Token="Toka" * 8)
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID,
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, ApiOid=self.API_OID_2,
                                   Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_many([mdl_api_1, mdl_api_2])
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        mdl = RootUserManager.get_root_data_api_oid(self.API_OID)
        self.assertEqual(mdl, mdl_root_1)
        mdl = RootUserManager.get_root_data_api_oid(self.API_OID_2)
        self.assertEqual(mdl, mdl_root_2)

    def test_get_root_data_api_oid_str_oid(self):
        mdl_api_1 = APIUserModel(Id=self.API_OID, Email=self.GOO_IDENTITY.email,
                                 GoogleUid=self.GOO_IDENTITY.uid, Token="Toke" * 8)
        mdl_api_2 = APIUserModel(Id=self.API_OID_2, Email=self.GOO_IDENTITY_2.email,
                                 GoogleUid=self.GOO_IDENTITY_2.uid, Token="Toka" * 8)
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID,
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, ApiOid=self.API_OID_2,
                                   Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_many([mdl_api_1, mdl_api_2])
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        mdl = RootUserManager.get_root_data_api_oid(str(self.API_OID))
        self.assertEqual(mdl, mdl_root_1)
        mdl = RootUserManager.get_root_data_api_oid(str(self.API_OID_2))
        self.assertEqual(mdl, mdl_root_2)

    def test_get_root_data_api_oid_missed(self):
        mdl_api_1 = APIUserModel(Id=self.API_OID, Email=self.GOO_IDENTITY.email,
                                 GoogleUid=self.GOO_IDENTITY.uid, Token="Toke" * 8)
        mdl_api_2 = APIUserModel(Id=self.API_OID_2, Email=self.GOO_IDENTITY_2.email,
                                 GoogleUid=self.GOO_IDENTITY_2.uid, Token="Toka" * 8)
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, ApiOid=self.API_OID,
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, ApiOid=self.API_OID_2,
                                   Config=RootUserConfigModel.generate_default())
        APIUserManager.insert_many([mdl_api_1, mdl_api_2])
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        self.assertIsNone(RootUserManager.get_root_data_api_oid(ObjectId()))

    def test_get_root_data_api_oid_no_data(self):
        self.assertIsNone(RootUserManager.get_root_data_api_oid(self.ONPLAT_OID))

    def test_get_root_data_onplat_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(mdl_root_1, RootUserManager.get_root_data_onplat_oid(self.ONPLAT_OID))
        self.assertEqual(mdl_root_1, RootUserManager.get_root_data_onplat_oid(self.ONPLAT_OID_2))

    def test_get_root_data_onplat_oid_str_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(mdl_root_1, RootUserManager.get_root_data_onplat_oid(str(self.ONPLAT_OID)))
        self.assertEqual(mdl_root_1, RootUserManager.get_root_data_onplat_oid(str(self.ONPLAT_OID_2)))

    def test_get_root_data_onplat_oid_missed(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertIsNone(RootUserManager.get_root_data_onplat_oid(ObjectId()))

    def test_get_root_data_onplat_oid_no_data(self):
        self.assertIsNone(RootUserManager.get_root_data_onplat_oid(self.ONPLAT_OID))

    def test_get_tzinfo_root_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(DEFAULT_LOCALE.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(self.ROOT_OID))

    def test_get_tzinfo_root_oid_str_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(DEFAULT_LOCALE.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(str(self.ROOT_OID)))

    def test_get_tzinfo_root_oid_missed(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(DEFAULT_LOCALE.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(ObjectId()))

    def test_get_tzinfo_root_oid_no_data(self):
        self.assertEqual(DEFAULT_LOCALE.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(self.ROOT_OID))

    def test_get_lang_code_root_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default(Locale=USA_CENT.pytz_code))
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(USA_CENT.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(self.ROOT_OID))

    def test_get_lang_code_root_oid_str_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default(Locale=USA_CENT.pytz_code))
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(USA_CENT.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(str(self.ROOT_OID)))

    def test_get_lang_code_root_oid_missed(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default(Locale=USA_CENT.pytz_code))
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(DEFAULT_LOCALE.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(ObjectId()))

    def test_get_lang_code_root_oid_no_data(self):
        self.assertEqual(DEFAULT_LOCALE.to_tzinfo(), RootUserManager.get_tzinfo_root_oid(self.ROOT_OID))

    def test_get_config_root_oid(self):
        cfg_mdl = RootUserConfigModel.generate_default(Locale=USA_CENT.pytz_code)
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2], Config=cfg_mdl)
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(cfg_mdl, RootUserManager.get_config_root_oid(self.ROOT_OID))

    def test_get_config_root_oid_str_oid(self):
        cfg_mdl = RootUserConfigModel.generate_default(Locale=USA_CENT.pytz_code)
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2], Config=cfg_mdl)
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(cfg_mdl, RootUserManager.get_config_root_oid(str(self.ROOT_OID)))

    def test_get_config_root_oid_missed(self):
        cfg_mdl = RootUserConfigModel.generate_default(Locale=USA_CENT.pytz_code)
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2], Config=cfg_mdl)
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(RootUserConfigModel.generate_default(), RootUserManager.get_config_root_oid(ObjectId()))

    def test_get_config_root_oid_no_data(self):
        self.assertEqual(RootUserConfigModel.generate_default(), RootUserManager.get_config_root_oid(self.ROOT_OID))

    def test_merge_onplat_to_api_old_to_new(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, OnPlatOids=[self.ONPLAT_OID_3],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        self.assertEqual(
            RootUserManager.merge_onplat_to_api(self.ROOT_OID, self.ROOT_OID_2),
            OperationOutcome.O_COMPLETED
        )
        self.assertEqual(
            RootUserManager.find_one_casted(),
            RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID_3, self.ONPLAT_OID, self.ONPLAT_OID_2])
        )

    def test_merge_onplat_to_api_new_to_old(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, OnPlatOids=[self.ONPLAT_OID_3],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        self.assertEqual(
            RootUserManager.merge_onplat_to_api(self.ROOT_OID_2, self.ROOT_OID),
            OperationOutcome.O_COMPLETED
        )
        self.assertEqual(
            RootUserManager.find_one_casted(),
            RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2, self.ONPLAT_OID_3])
        )

    def test_merge_onplat_to_api_src_eq_dst(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(
            RootUserManager.merge_onplat_to_api(self.ROOT_OID, self.ROOT_OID),
            OperationOutcome.X_SAME_SRC_DEST
        )
        self.assertEqual(RootUserManager.find_one(), mdl_root_1)

    def test_merge_onplat_to_api_has_api(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID], ApiOid=self.API_OID,
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, OnPlatOids=[self.ONPLAT_OID_3],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        self.assertEqual(
            RootUserManager.merge_onplat_to_api(self.ROOT_OID_2, self.ROOT_OID),
            OperationOutcome.O_COMPLETED
        )
        self.assertEqual(
            RootUserManager.find_one_casted(),
            RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_3], ApiOid=self.API_OID,
                          Config=RootUserConfigModel.generate_default())
        )

    def test_merge_onplat_to_api_str_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        mdl_root_2 = RootUserModel(Id=self.ROOT_OID_2, OnPlatOids=[self.ONPLAT_OID_3],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_many([mdl_root_1, mdl_root_2])

        self.assertEqual(
            RootUserManager.merge_onplat_to_api(str(self.ROOT_OID), str(self.ROOT_OID_2)),
            OperationOutcome.O_COMPLETED
        )
        self.assertEqual(
            RootUserManager.find_one_casted(),
            RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID_3, self.ONPLAT_OID, self.ONPLAT_OID_2],
                          Config=RootUserConfigModel.generate_default())
        )

    def test_merge_onplat_to_api_missed(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        self.assertEqual(
            RootUserManager.merge_onplat_to_api(self.ROOT_OID, self.ROOT_OID_2),
            OperationOutcome.X_DEST_DATA_NOT_FOUND
        )
        self.assertEqual(
            RootUserManager.find_one({OID_KEY: self.ROOT_OID}),
            RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2])
        )
        self.assertEqual(
            RootUserManager.merge_onplat_to_api(self.ROOT_OID_2, self.ROOT_OID),
            OperationOutcome.X_SRC_DATA_NOT_FOUND
        )
        self.assertEqual(
            RootUserManager.find_one({OID_KEY: self.ROOT_OID}),
            RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2])
        )

    def test_merge_onplat_to_api_no_data(self):
        self.assertEqual(
            RootUserManager.merge_onplat_to_api(self.ROOT_OID, self.ROOT_OID_2),
            OperationOutcome.X_SRC_DATA_NOT_FOUND
        )

    def test_update_config(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        result = RootUserManager.update_config(self.ROOT_OID, Name="UserName")
        expected_mdl = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                     Config=RootUserConfigModel.generate_default(Name="UserName"))
        self.assertEqual(result.outcome, UpdateOutcome.O_UPDATED)
        self.assertTrue(result.success)
        self.assertEqual(result.model, expected_mdl)
        self.assertEqual(RootUserManager.find_one({OID_KEY: self.ROOT_OID}), expected_mdl)

    def test_update_config_str_oid(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        result = RootUserManager.update_config(str(self.ROOT_OID), Name="UserName")
        expected_mdl = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                     Config=RootUserConfigModel.generate_default(Name="UserName"))
        self.assertEqual(result.outcome, UpdateOutcome.O_UPDATED)
        self.assertTrue(result.success)
        self.assertEqual(result.model, expected_mdl)
        self.assertEqual(RootUserManager.find_one({OID_KEY: self.ROOT_OID}), expected_mdl)

    def test_update_config_key_not_exists(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        result = RootUserManager.update_config(str(self.ROOT_OID), Kkkey="Vvvalue")
        expected_mdl = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                     Config=RootUserConfigModel.generate_default())
        self.assertEqual(result.outcome, UpdateOutcome.O_UPDATED)
        self.assertTrue(result.success)
        self.assertEqual(result.model, expected_mdl)
        self.assertEqual(RootUserManager.find_one({OID_KEY: self.ROOT_OID}), expected_mdl)

    def test_update_config_missed(self):
        mdl_root_1 = RootUserModel(Id=self.ROOT_OID, OnPlatOids=[self.ONPLAT_OID, self.ONPLAT_OID_2],
                                   Config=RootUserConfigModel.generate_default())
        RootUserManager.insert_one(mdl_root_1)

        result = RootUserManager.update_config(ObjectId(), Name="UserName")
        self.assertEqual(result.outcome, UpdateOutcome.X_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)
        self.assertEqual(RootUserManager.find_one({OID_KEY: self.ROOT_OID}), mdl_root_1)

    def test_update_config_no_data(self):
        result = RootUserManager.update_config(self.ROOT_OID, Name="UserName")
        self.assertEqual(result.outcome, UpdateOutcome.X_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)
        self.assertIsNone(RootUserManager.find_one({OID_KEY: self.ROOT_OID}))
