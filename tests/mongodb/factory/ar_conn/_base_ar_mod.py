from datetime import datetime

from bson import ObjectId

from flags import AutoReplyContentType, PermissionLevel, ProfilePermission, Platform
from models import AutoReplyContentModel, AutoReplyModuleModel
from mongodb.factory import ProfileManager, ChannelManager
from mongodb.factory.ar_conn import AutoReplyModuleManager
from tests.base import TestDatabaseMixin, TestTimeComparisonMixin, TestModelMixin


class TestArModuleSample(TestDatabaseMixin):
    """
    There are a few sample models can be used in this test.

    -------------

    These models can be briefly described as follows

    - 1st model: Keyword = A / Response = B / Cooldown = 0 / No Tag / Not Private
    - 2nd model: Keyword = A / Response = C / Cooldown = 0 / No Tag / Not Private
    - 3rd model: Keyword = A / Response = D / Cooldown = 1 / Has Tag / Is Private (Args no cooldown, tag, not private)
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
    - 14th model: invalid param (additional not in use)
    - 15th model: response sticker ID invalid
    - 16th model: negative cooldown
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
        cooldown = 1

        return {
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
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
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }

    def get_mdl_16_args(self):
        keyword = AutoReplyContentModel(Content="F", ContentType=AutoReplyContentType.TEXT)
        responses = [AutoReplyContentModel(Content="1", ContentType=AutoReplyContentType.LINE_STICKER)]
        creator_oid = self.CREATOR_OID
        channel_oid = self.channel_oid
        pinned = False
        private = False
        tag_ids = []
        cooldown = -5

        return {
            "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
            "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
        }


class TestArModuleManagerBase(TestArModuleSample, TestTimeComparisonMixin, TestDatabaseMixin, TestModelMixin):
    inst = None

    @classmethod
    def setUpTestClass(cls):
        cls.inst = AutoReplyModuleManager()

    def grant_access_pin_permission(self):
        reg_result = ChannelManager.ensure_register(Platform.LINE, "U123456")
        if reg_result.success:
            self.channel_oid = reg_result.model.id
        else:
            self.fail(reg_result.outcome)

        prof = ProfileManager.register_new(
            self.CREATOR_OID, {"ChannelOid": self.channel_oid, "PermissionLevel": PermissionLevel.ADMIN})
        ProfileManager.attach_profile(self.channel_oid, self.CREATOR_OID, prof.get_oid())

        perms = ProfileManager.get_user_permissions(self.channel_oid, self.CREATOR_OID)

        if ProfilePermission.AR_ACCESS_PINNED_MODULE not in perms:
            self.fail("Permission to access pinned module not granted.")

    def _add_call_module_kw_a(self):
        """
        This method perform actions in the following order:

        - Add a module ``Keyword=A, Responses=B``

        - Call the above module 4 times

        - Add a module ``Keyword=A, Responses=C``, overwriting the module mentioned in ``1.``

        - Call the above module 3 times

        - Add a module ``Keyword=A, Responses=D``, overwriting the module mentioned in ``2.``

        - Return the OIDs of these modules in order.

        OID is specified because that overwriting a module will permanently delete them.

        OIDs used are ``datetime(2020, 5, 1)``, ``datetime(2020, 5, 2)`` and ``datetime(2020, 5, 3)``.

        :return: OIDs of the module added
        """
        # noinspection PyListCreation
        oids = []

        oids.append(
            self.inst.add_conn(
                Keyword=AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
                Id=ObjectId.from_datetime(datetime(2020, 5, 1))
            ).model.id)
        self.inst.get_conn("A", AutoReplyContentType.TEXT, self.channel_oid)
        self.inst.get_conn("A", AutoReplyContentType.TEXT, self.channel_oid)
        self.inst.get_conn("A", AutoReplyContentType.TEXT, self.channel_oid)
        self.inst.get_conn("A", AutoReplyContentType.TEXT, self.channel_oid)

        oids.append(
            self.inst.add_conn(
                Keyword=AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
                Id=ObjectId.from_datetime(datetime(2020, 5, 2))
            ).model.id)
        self.inst.get_conn("A", AutoReplyContentType.TEXT, self.channel_oid)
        self.inst.get_conn("A", AutoReplyContentType.TEXT, self.channel_oid)
        self.inst.get_conn("A", AutoReplyContentType.TEXT, self.channel_oid)

        oids.append(
            self.inst.add_conn(
                Keyword=AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT),
                Responses=[AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT)],
                CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
                Id=ObjectId.from_datetime(datetime(2020, 5, 3))
            ).model.id)

        return oids

    def _add_call_module_multi(self):
        """
        This method perform actions in the following order:

        -  Actions in ``_add_call_module_kw_a()``

        -  Add a module ``Keyword=B, Responses=C``

        -  Call the above module 9 times

        -  Add a module ``Keyword=C, Responses=C``

        -  Add a module ``Keyword=D, Responses=C``

        OID is specified because that overwriting a module will permanently delete them.

        OIDs used are any OIDs used in ``_add_call_module_kw_a()`` and
        ``datetime(2020, 5, 4)``, ``datetime(2020, 5, 5)``, ``datetime(2020, 5, 6)`` and  ``datetime(2020, 5, 7)``.
        """
        self._add_call_module_kw_a()

        self.inst.add_conn(
            Keyword=AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT),
            Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
            CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
            Id=ObjectId.from_datetime(datetime(2020, 5, 4))
        )
        for _ in range(9):
            self.inst.get_conn("B", AutoReplyContentType.TEXT, self.channel_oid)

        self.inst.add_conn(
            Keyword=AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT),
            Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
            CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
            Id=ObjectId.from_datetime(datetime(2020, 5, 5))
        )

        self.inst.add_conn(
            Keyword=AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT),
            Responses=[AutoReplyContentModel(Content="E", ContentType=AutoReplyContentType.TEXT)],
            CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
            Id=ObjectId.from_datetime(datetime(2020, 5, 6))
        )

        self.inst.add_conn(
            Keyword=AutoReplyContentModel(Content="D", ContentType=AutoReplyContentType.TEXT),
            Responses=[AutoReplyContentModel(Content="C", ContentType=AutoReplyContentType.TEXT)],
            CreatorOid=self.CREATOR_OID, ChannelOid=self.channel_oid,
            Id=ObjectId.from_datetime(datetime(2020, 5, 7))
        )
