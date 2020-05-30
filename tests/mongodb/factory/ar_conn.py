from datetime import datetime

from bson import ObjectId

from flags import AutoReplyContentType, PermissionLevel, ProfilePermission, Platform
from models import AutoReplyContentModel, AutoReplyModuleModel
from models.exceptions import FieldKeyNotExistError
from mongodb.factory.results import WriteOutcome
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.factory.ar_conn import AutoReplyModuleManager
from tests.base import TestDatabaseMixin

__all__ = ["TestArModuleManager"]


class _TestArModuleSample(TestDatabaseMixin):
    """
    There are a few sample models can be used in this test.

    -------------

    These models can be briefly described as follows

    - 1st model: Keyword = A / Response = B / Cooldown = 0 / No Tag / Not Private
    - 2nd model: Keyword = A / Response = C / Cooldown = 0 / No Tag / Not Private
    - 3rd model: Keyword = A / Response = D / Cooldown = 10 / Has Tag / Is Private (Args no cooldown, tag, not private)
    - 4th model: Keyword = D / Response = B
    - 5th model: Keyword = E / Response = F / Is Pinned
    - 6th model: Keyword = E / Response = G / Not Pinned
    - 7th model: Keyword = E / Response = F / Not Pinned
    - 8th model: keyword sticker ID invalid
    - 9th model: keyword image URL invalid
    - 10th model: Keyword = E / Response = G / Is Pinned
    - 11th model: Keyword = E / Response = G / Is Pinned / Creator II
    - 12th model: Keyword = 1 (Text) / Response A
    - 13th model: Keyword = 1 (Sticker) / Response A
    - 14th model: invalid param
    - 15th model: response sticker ID invalid
    """

    CREATOR_OID = ObjectId()
    CREATOR_OID_2 = ObjectId()

    def setUpTestCase(self) -> None:
        self.channel_oid = ObjectId()

    def get_mdl_1_args(self):
        keyword = AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_1(self):
        return AutoReplyModuleModel(**self.get_mdl_1_args())

    def get_mdl_2_args(self):
        keyword = AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_2(self):
        return AutoReplyModuleModel(**self.get_mdl_2_args())

    def get_mdl_3_args(self):
        keyword = AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = True
        tag_ids = [ObjectId(), ObjectId()]
        cooldown = 10

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_3(self):
        return AutoReplyModuleModel(**self.get_mdl_3_args())

    def get_mdl_4_args(self):
        keyword = AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_4(self):
        return AutoReplyModuleModel(**self.get_mdl_4_args())

    def get_mdl_5_args(self):
        keyword = AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = True
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_5(self):
        return AutoReplyModuleModel(**self.get_mdl_5_args())

    def get_mdl_6_args(self):
        keyword = AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="G", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_6(self):
        return AutoReplyModuleModel(**self.get_mdl_6_args())

    def get_mdl_7_args(self):
        keyword = AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = True
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_7(self):
        return AutoReplyModuleModel(**self.get_mdl_7_args())

    def get_mdl_8_args(self):
        keyword = AutoReplyContentModel(Content="87", ContentType=AutoReplyContentType.LINE_STICKER)
        responses = [AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_9_args(self):
        keyword = AutoReplyContentModel(Content="https://google.png", ContentType=AutoReplyContentType.IMAGE)
        responses = [AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_10_args(self):
        keyword = AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="G", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = True
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_10(self):
        return AutoReplyModuleModel(**self.get_mdl_10_args())

    def get_mdl_11_args(self):
        keyword = AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="G", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID_2
        channel_oid = self.channel_oid
        pinned = True
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_11(self):
        return AutoReplyModuleModel(**self.get_mdl_11_args())

    def get_mdl_12_args(self):
        keyword = AutoReplyContentModel(Content="1", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_12(self):
        return AutoReplyModuleModel(**self.get_mdl_12_args())

    def get_mdl_13_args(self):
        keyword = AutoReplyContentModel(Content="1", ContentType=AutoReplyContentType.LINE_STICKER)
        responses = [AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_13(self):
        return AutoReplyModuleModel(**self.get_mdl_13_args())

    def get_mdl_14_args(self):
        keyword = AutoReplyContentModel(Content="1", ContentType=AutoReplyContentType.LINE_STICKER)
        responses = [AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown, "A": "C"
        }

    def get_mdl_15_args(self):
        keyword = AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="87", ContentType=AutoReplyContentType.LINE_STICKER)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = 0

        return {
            "Keyword": keyword, "Responses": responses, "ChannelId": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }


class TestArModuleManager(_TestArModuleSample, TestDatabaseMixin):
    inst = None

    @classmethod
    def setUpTestClass(cls):
        cls.inst = AutoReplyModuleManager()

    def grant_access_pin_permission(self):
        self.channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        prof = ProfileManager.register_new(
            self.CREATOR_OID, {"ChannelOid": self.channel_oid, "PermissionLevel": PermissionLevel.ADMIN})
        ProfileManager.attach_profile(self.channel_oid, self.CREATOR_OID, prof.get_oid())

        perms = ProfileManager.get_user_permissions(self.channel_oid, self.CREATOR_OID)

        if ProfilePermission.AR_ACCESS_PINNED_MODULE not in perms:
            self.fail("Permission to access pinned module not granted.")

    def test_add_single_not_pinned(self):
        result = self.inst.add_conn(**self.get_mdl_1_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_1())

        mdl = self.inst.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_1())

    def test_add_duplicated_kw_overwrite(self):
        self.inst.add_conn(**self.get_mdl_1_args())
        result = self.inst.add_conn(**self.get_mdl_2_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_2())

        mdl = self.inst.get_conn(
            self.get_mdl_2().keyword.content, self.get_mdl_2().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_2())

    def test_add_duplicated_response(self):
        self.inst.add_conn(**self.get_mdl_1_args())
        result = self.inst.add_conn(**self.get_mdl_4_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_4())

        mdl = self.inst.get_conn(
            self.get_mdl_4().keyword.content, self.get_mdl_4().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_4())

    def test_add_kw_invalid_sticker_id(self):
        result = self.inst.add_conn(**self.get_mdl_8_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_KEYWORD)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = self.inst.get_conn(
            self.get_mdl_9_args()["Keyword"].content, self.get_mdl_9_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_resp_invalid_sticker_id(self):
        result = self.inst.add_conn(**self.get_mdl_15_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_RESPONSE)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = self.inst.get_conn(
            self.get_mdl_15_args()["Keyword"].content, self.get_mdl_15_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_kw_invalid_image_url(self):
        result = self.inst.add_conn(**self.get_mdl_9_args())

        self.assertEqual(result.outcome, WriteOutcome.X_AR_INVALID_KEYWORD)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = self.inst.get_conn(
            self.get_mdl_9_args()["Keyword"].content, self.get_mdl_9_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_invalid_param(self):
        result = self.inst.add_conn(**self.get_mdl_14_args())

        self.assertEqual(result.outcome, WriteOutcome.X_MODEL_KEY_NOT_EXIST)
        self.assertIsInstance(result.exception, FieldKeyNotExistError)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = self.inst.get_conn(
            self.get_mdl_14_args()["Keyword"].content, self.get_mdl_14_args()["Keyword"].content_type,
            self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_back_after_del(self):
        # Add one first
        self.inst.add_conn(**self.get_mdl_1_args())

        # Delete one and test get
        self.inst.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.channel_oid, TestArModuleManager.CREATOR_OID)
        mdl = self.inst.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.channel_oid)
        self.assertIsNone(mdl)

        # Add the same back
        result = self.inst.add_conn(**self.get_mdl_1_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_1())

        mdl = self.inst.get_conn(
            self.get_mdl_1().keyword.content, self.get_mdl_1().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_1())

    def test_add_inherit_from_active(self):
        kwargs = self.get_mdl_3_args()
        self.inst.add_conn(**kwargs)

        result = self.inst.add_conn(**self.get_mdl_2_args())
        # Not using `self.get_mdl_3()` to preserve some OIDs because it will generated on called
        mdl_expected = AutoReplyModuleModel(**kwargs)
        mdl_expected.responses = self.get_mdl_2().responses

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, mdl_expected)

        mdl = self.inst.get_conn(
            self.get_mdl_3().keyword.content, self.get_mdl_3().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, mdl_expected)

    def test_add_inherit_original_inactive(self):
        self.inst.add_conn(**self.get_mdl_3_args())
        self.inst.module_mark_inactive(
            self.get_mdl_3().keyword.content, self.channel_oid, TestArModuleManager.CREATOR_OID)

        result = self.inst.add_conn(**self.get_mdl_2_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_2())

        mdl = self.inst.get_conn(
            self.get_mdl_2().keyword.content, self.get_mdl_2().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_2())

    def test_add_pinned_has_permission(self):
        self.grant_access_pin_permission()

        result = self.inst.add_conn(**self.get_mdl_5_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_5())

        mdl = self.inst.get_conn(
            self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_5())

    def test_add_pinned_overwrite_has_permission(self):
        self.grant_access_pin_permission()

        self.inst.add_conn(**self.get_mdl_5_args())
        result = self.inst.add_conn(**self.get_mdl_10_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_10())

        mdl = self.inst.get_conn(
            self.get_mdl_10().keyword.content, self.get_mdl_10().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_10())

    def test_add_pinned_no_permission(self):
        result = self.inst.add_conn(**self.get_mdl_5_args())

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = self.inst.get_conn(
            self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.channel_oid)
        self.assertIsNone(mdl)

    def test_add_pinned_overwrite_no_permission(self):
        self.grant_access_pin_permission()

        self.inst.add_conn(**self.get_mdl_5_args())
        result = self.inst.add_conn(**self.get_mdl_11_args())

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = self.inst.get_conn(
            self.get_mdl_11().keyword.content, self.get_mdl_11().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_5())

    def test_add_pinned_overwrite_not_pinned(self):
        self.grant_access_pin_permission()

        self.inst.add_conn(**self.get_mdl_5_args())
        result = self.inst.add_conn(**self.get_mdl_6_args())

        self.assertEqual(result.outcome, WriteOutcome.X_PINNED_CONTENT_EXISTED)
        self.assertIsNone(result.exception)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        mdl = self.inst.get_conn(
            self.get_mdl_6().keyword.content, self.get_mdl_6().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_5())

    def test_add_same_content_different_type(self):
        result = self.inst.add_conn(**self.get_mdl_12_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_12())

        mdl = self.inst.get_conn(
            self.get_mdl_12().keyword.content, self.get_mdl_12().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_12())

        result = self.inst.add_conn(**self.get_mdl_13_args())

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertIsNone(result.exception)
        self.assertTrue(result.success)
        result.model.clear_oid()
        self.assertEqual(result.model, self.get_mdl_13())

        mdl = self.inst.get_conn(
            self.get_mdl_13().keyword.content, self.get_mdl_13().keyword.content_type, self.channel_oid)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_13())

    def test_add_short_time_overwrite_perma_remove(self):
        self.inst.add_conn(**self.get_mdl_1_args())
        mdl = self.inst.add_conn(**self.get_mdl_2_args()).model

        self.assertEqual(self.inst.count_documents({}), 1)
        self.assertEqual(self.inst.find_one(), mdl)

    def test_del_short_time_overwrite_perma_remove(self):
        self.inst.add_conn(**self.get_mdl_1_args())

        self.inst.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_id, self.get_mdl_1().creator_oid)

        self.assertEqual(self.inst.count_documents({}), 0)

    def test_add_long_time_overwrite_preserve(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        self.inst.add_conn(**args)

        self.inst.add_conn(**self.get_mdl_2_args())

        self.assertEqual(self.inst.count_documents({}), 2)

    def test_del_long_time_overwrite_preserve(self):
        args = self.get_mdl_1_args()
        args["Id"] = ObjectId.from_datetime(datetime(2020, 5, 1))
        self.inst.add_conn(**args)

        self.inst.module_mark_inactive(
            self.get_mdl_1().keyword.content, self.get_mdl_1().channel_id, self.get_mdl_1().creator_oid)

        self.assertEqual(self.inst.count_documents({}), 1)

    def test_del_pinned_has_permission(self):
        self.grant_access_pin_permission()

        self.inst.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            self.inst.module_mark_inactive(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_id, self.get_mdl_5().creator_oid),
            WriteOutcome.O_DATA_UPDATED)

        self.assertIsNone(
            self.inst.get_conn(
                self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.get_mdl_5().channel_id))

    def test_del_pinned_no_permission(self):
        self.grant_access_pin_permission()
        self.inst.add_conn(**self.get_mdl_5_args())

        self.assertEqual(
            self.inst.module_mark_inactive(
                self.get_mdl_5().keyword.content, self.get_mdl_5().channel_id, self.CREATOR_OID_2),
            WriteOutcome.X_INSUFFICIENT_PERMISSION)

        mdl = self.inst.get_conn(
            self.get_mdl_5().keyword.content, self.get_mdl_5().keyword.content_type, self.get_mdl_5().channel_id)
        mdl.clear_oid()
        self.assertEqual(mdl, self.get_mdl_5())

    def test_del_mark_remover_and_time(self):
        pass

    def test_del_not_found(self):
        pass

    def test_get_count_call(self):
        pass

    def test_get_after_add_multi(self):
        pass

    def test_get_list_by_keyword(self):
        pass

    def test_get_list_by_oids(self):
        pass

    def test_stats_module_count(self):
        pass

    def test_stats_unique_count(self):
        pass
