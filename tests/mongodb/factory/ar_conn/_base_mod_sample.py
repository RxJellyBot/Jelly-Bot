from abc import ABC
from functools import lru_cache

from bson import ObjectId

from flags import AutoReplyContentType
from models import AutoReplyContentModel, AutoReplyModuleModel
from tests.base import TestDatabaseMixin

__all__ = ["TestArModuleSample"]


class TestArModuleSample(ABC):
    class TestClass(TestDatabaseMixin):
        """
        There are a few sample models can be used in this test.

        -------------

        These models can be briefly described as follows

        - 1st model: Keyword = A / Response = B / Cooldown = 0 / No Tag / Not Private
        - 2nd model: Keyword = A / Response = C / Cooldown = 0 / No Tag / Not Private
        - 3rd model:
            Keyword = A / Response = D / Cooldown = 1 / Has Tag / Is Private (Args no cooldown, tag, not private)
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
        - 17th model: cooldown = 100
        """

        CREATOR_OID = ObjectId()
        CREATOR_OID_2 = ObjectId()

        def setUpTestCase(self) -> None:
            self.channel_oid = ObjectId()

        @lru_cache(maxsize=None)
        def get_mdl_1_args(self):
            """
            Keyword: ``A``

            Response: ``[B]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_1(self):
            """
            Keyword: ``A``

            Response: ``[B]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_1_args())

        @lru_cache(maxsize=None)
        def get_mdl_2_args(self):
            """
            Keyword: ``A``

            Response: ``[C]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_2(self):
            """
            Keyword: ``A``

            Response: ``[C]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_2_args())

        @lru_cache(maxsize=None)
        def get_mdl_3_args(self):
            """
            Keyword: ``A``

            Response: ``[D]``

            Creator: #1

            Pinned: ``False``

            Private: ``True``

            Tag #: ``2``

            Cooldown: ``1``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_3(self):
            """
            Keyword: ``A``

            Response: ``[D]``

            Creator: #1

            Pinned: ``False``

            Private: ``True``

            Tag #: ``2``

            Cooldown: ``3``
            """
            return AutoReplyModuleModel(**self.get_mdl_3_args())

        @lru_cache(maxsize=None)
        def get_mdl_4_args(self):
            """
            Keyword: ``D``

            Response: ``[B]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_4(self):
            """
            Keyword: ``D``

            Response: ``[B]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_4_args())

        @lru_cache(maxsize=None)
        def get_mdl_5_args(self):
            """
            Keyword: ``E``

            Response: ``[F]``

            Creator: #1

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_5(self):
            """
            Keyword: ``E``

            Response: ``[F]``

            Creator: #1

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_5_args())

        @lru_cache(maxsize=None)
        def get_mdl_6_args(self):
            """
            Keyword: ``E``

            Response: ``[G]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_6(self):
            """
            Keyword: ``E``

            Response: ``[G]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_6_args())

        @lru_cache(maxsize=None)
        def get_mdl_7_args(self):
            """
            Keyword: ``E``

            Response: ``[F]``

            Creator: #1

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_7(self):
            """
            Keyword: ``E``

            Response: ``[F]``

            Creator: #1

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_7_args())

        @lru_cache(maxsize=None)
        def get_mdl_8_args(self):
            """
            Keyword: ``(Invalid sticker ID)``

            Response: ``[F]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_9_args(self):
            """
            Keyword: ``(Invalid image URL)``

            Response: ``[F]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_10_args(self):
            """
            Keyword: ``E``

            Response: ``[G]``

            Creator: #1

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_10(self):
            """
            Keyword: ``E``

            Response: ``[G]``

            Creator: #1

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_10_args())

        @lru_cache(maxsize=None)
        def get_mdl_11_args(self):
            """
            Keyword: ``E``

            Response: ``[G]``

            Creator: #2

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_11(self):
            """
            Keyword: ``E``

            Response: ``[G]``

            Creator: #2

            Pinned: ``True``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_11_args())

        @lru_cache(maxsize=None)
        def get_mdl_12_args(self):
            """
            Keyword: ``1 (Text)``

            Response: ``[A]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_12(self):
            """
            Keyword: ``1 (Text)``

            Response: ``[A]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_12_args())

        @lru_cache(maxsize=None)
        def get_mdl_13_args(self):
            """
            Keyword: ``1 (Sticker)``

            Response: ``[A]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_13(self):
            """
            Keyword: ``1 (Sticker)``

            Response: ``[A]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
            return AutoReplyModuleModel(**self.get_mdl_13_args())

        @lru_cache(maxsize=None)
        def get_mdl_14_args(self):
            """
            Additional not-in-use parameter.
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_15_args(self):
            """
            Keyword: ``F``

            Response: ``[(Invalid sticker ID)]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``0``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_16_args(self):
            """
            Keyword: ``F``

            Response: ``[1 (Sticker)]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``-5``
            """
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

        @lru_cache(maxsize=None)
        def get_mdl_17_args(self):
            """
            Keyword: ``A``

            Response: ``[B]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``100``
            """
            keyword = AutoReplyContentModel(Content="A", ContentType=AutoReplyContentType.TEXT)
            responses = [AutoReplyContentModel(Content="B", ContentType=AutoReplyContentType.TEXT)]
            creator_oid = self.CREATOR_OID
            channel_oid = self.channel_oid
            pinned = False
            private = False
            tag_ids = []
            cooldown = 100

            return {
                "Keyword": keyword, "Responses": responses, "ChannelOid": channel_oid, "CreatorOid": creator_oid,
                "Pinned": pinned, "Private": private, "TagIds": tag_ids, "CooldownSec": cooldown
            }

        @lru_cache(maxsize=None)
        def get_mdl_17(self):
            """
            Keyword: ``A``

            Response: ``[B]``

            Creator: #1

            Pinned: ``False``

            Private: ``False``

            Tag #: ``0``

            Cooldown: ``100``
            """
            return AutoReplyModuleModel(**self.get_mdl_17_args())
