from datetime import datetime

import pytz
from bson import ObjectId
from django.conf import settings

from extutils.emailutils import EmailServer
from flags import Platform, MessageType
from models import (
    ChannelModel, ChannelConfigModel, ChannelProfileConnectionModel, MessageRecordModel, RootUserModel,
    RootUserConfigModel, OnPlatformUserModel
)
from mongodb.factory import ChannelManager, MessageRecordStatisticsManager, RootUserManager
from mongodb.factory.prof_base import UserProfileManager
from mongodb.factory.user import OnPlatformIdentityManager
from mongodb.helper import IdentitySearcher
from tests.base import TestCase

__all__ = ("TestIdentitySearcher",)


class TestIdentitySearcher(TestCase):
    CHANNEL_1_OID = ObjectId()
    CHANNEL_2_OID = ObjectId()
    CHANNEL_3_OID = ObjectId()

    PROF_1_OID = ObjectId()
    PROF_2_OID = ObjectId()
    PROF_3_OID = ObjectId()

    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()

    ONPLAT_OID = ObjectId()

    API_OID = ObjectId()
    API_OID_2 = ObjectId()

    LINE_TOKEN = "U4c94d18c660743c963fd3a08a025b8b3"  # Actually exists
    LINE_NAME = "RaenonX"  # Actually exists

    CHANNEL_1 = ChannelModel(
        Id=CHANNEL_1_OID, Platform=Platform.LINE, Token="C123456",
        Config=ChannelConfigModel.generate_default(DefaultProfileOid=PROF_1_OID, DefaultName="CHANNEL #1")
    )
    CHANNEL_2 = ChannelModel(
        Id=CHANNEL_2_OID, Platform=Platform.LINE, Token="C789012",
        Config=ChannelConfigModel.generate_default(DefaultProfileOid=PROF_2_OID, DefaultName="CHANNEL #2")
    )
    CHANNEL_3 = ChannelModel(
        Id=CHANNEL_3_OID, Platform=Platform.LINE, Token="C345678",
        Config=ChannelConfigModel.generate_default(DefaultProfileOid=PROF_3_OID, DefaultName="#3")
    )
    CHANNEL_4 = ChannelModel(
        Id=ObjectId("5dd1bd8290ff56e291b72e65"), Platform=Platform.LINE, Token="C2525832a417beda4e9cde5c335620736",
        Config=ChannelConfigModel(DefaultProfileOid=ObjectId())
    )  # Actually exists

    @staticmethod
    def obj_to_clear():
        return [ChannelManager, UserProfileManager, RootUserManager, MessageRecordStatisticsManager, EmailServer]

    def _insert_messages(self):
        mdls = [
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 5, 31, 5, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_1_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M4", ProcessTimeSecs=2.13),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 5, 31, 6, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_1_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M3", ProcessTimeSecs=2.13),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 5, 31, 3, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_2_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M2", ProcessTimeSecs=2.13),
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 5, 31, 4, tzinfo=pytz.utc)),
                               ChannelOid=self.CHANNEL_2_OID, UserRootOid=self.USER_OID,
                               MessageType=MessageType.TEXT, MessageContent="M1", ProcessTimeSecs=2.13),
        ]

        MessageRecordStatisticsManager.insert_many(mdls)

        return mdls

    def test_search_channel_by_default_name(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3])
        UserProfileManager.insert_many([
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_1_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_1_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_2_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_2_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_3_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3_OID])
        ])

        result = IdentitySearcher.search_channel("CHANNEL", self.USER_OID)

        self.assertEqual(len(result), 2)
        entry = result[0]
        self.assertEqual(entry.channel_name, "CHANNEL #2")
        self.assertEqual(entry.channel_model, self.CHANNEL_2)
        entry = result[1]
        self.assertEqual(entry.channel_name, "CHANNEL #1")
        self.assertEqual(entry.channel_model, self.CHANNEL_1)

    def test_search_channel_by_token(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3])
        UserProfileManager.insert_many([
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_1_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_1_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_2_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_2_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_3_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3_OID])
        ])

        result = IdentitySearcher.search_channel("345", self.USER_OID)

        self.assertEqual(len(result), 2)
        entry = result[0]
        self.assertEqual(entry.channel_name, "#3")
        self.assertEqual(entry.channel_model, self.CHANNEL_3)
        entry = result[1]
        self.assertEqual(entry.channel_name, "CHANNEL #1")
        self.assertEqual(entry.channel_model, self.CHANNEL_1)

    def test_search_channel_by_message(self):
        self._insert_messages()

        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3])
        UserProfileManager.insert_many([
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_1_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_1_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_2_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_2_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_3_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3_OID])
        ])

        result = IdentitySearcher.search_channel("M", self.USER_OID)

        self.assertEqual(len(result), 2)
        entry = result[0]
        self.assertEqual(entry.channel_name, "CHANNEL #1")
        self.assertEqual(entry.channel_model, self.CHANNEL_1)
        entry = result[1]
        self.assertEqual(entry.channel_name, "CHANNEL #2")
        self.assertEqual(entry.channel_model, self.CHANNEL_2)

    def test_search_channel_msg_hanging_cid(self):
        self._insert_messages()

        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_3])
        UserProfileManager.insert_many([
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_1_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_1_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_2_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_2_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_3_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3_OID])
        ])

        result = IdentitySearcher.search_channel("M", self.USER_OID)

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry.channel_name, "CHANNEL #1")
        self.assertEqual(entry.channel_model, self.CHANNEL_1)

        self.assertEqual(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 1)

    def test_search_channel_sort_mixed(self):
        self._insert_messages()

        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3])
        UserProfileManager.insert_many([
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_1_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_1_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_2_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_2_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_3_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3_OID])
        ])

        result = IdentitySearcher.search_channel("#", self.USER_OID)

        self.assertEqual(len(result), 3)
        entry = result[0]
        self.assertEqual(entry.channel_name, "CHANNEL #1")
        self.assertEqual(entry.channel_model, self.CHANNEL_1)
        entry = result[1]
        self.assertEqual(entry.channel_name, "CHANNEL #2")
        self.assertEqual(entry.channel_model, self.CHANNEL_2)
        entry = result[2]
        self.assertEqual(entry.channel_name, "#3")
        self.assertEqual(entry.channel_model, self.CHANNEL_3)

    def test_search_channel_empty_keyword(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3])
        UserProfileManager.insert_many([
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_1_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_1_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_2_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_2_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_3_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3_OID])
        ])

        result = IdentitySearcher.search_channel("", self.USER_OID)

        self.assertEqual(len(result), 3)
        entry = result[0]
        self.assertEqual(entry.channel_name, "#3")
        self.assertEqual(entry.channel_model, self.CHANNEL_3)
        entry = result[1]
        self.assertEqual(entry.channel_name, "CHANNEL #2")
        self.assertEqual(entry.channel_model, self.CHANNEL_2)
        entry = result[2]
        self.assertEqual(entry.channel_name, "CHANNEL #1")
        self.assertEqual(entry.channel_model, self.CHANNEL_1)

    def test_search_channel_user_missed(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3])
        UserProfileManager.insert_many([
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_1_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_1_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_2_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_2_OID]),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_3_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3_OID])
        ])

        result = IdentitySearcher.search_channel("", ObjectId())

        self.assertEqual(len(result), 0)

    def test_search_channel_no_data(self):
        result = IdentitySearcher.search_channel("", self.USER_OID)

        self.assertEqual(len(result), 0)

    def test_get_batch_user_name(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4])
        RootUserManager.insert_many([
            RootUserModel(Id=self.USER_OID, OnPlatOids=[self.ONPLAT_OID],
                          Config=RootUserConfigModel.generate_default()),
            RootUserModel(Id=self.USER_OID_2, ApiOid=self.API_OID,
                          Config=RootUserConfigModel.generate_default())
        ])
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        )

        result = IdentitySearcher.get_batch_user_name([self.USER_OID, self.USER_OID_2], self.CHANNEL_4)
        self.assertEqual(
            result,
            {
                self.USER_OID: self.LINE_NAME,
                self.USER_OID_2: f"UID - {self.USER_OID_2}"
            }
        )

    def test_get_batch_user_name_partial_user_not_exists(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4])
        RootUserManager.insert_many([
            RootUserModel(Id=self.USER_OID, OnPlatOids=[self.ONPLAT_OID],
                          Config=RootUserConfigModel.generate_default())
        ])
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        )

        result = IdentitySearcher.get_batch_user_name([self.USER_OID, self.USER_OID_2], self.CHANNEL_4)
        self.assertEqual(
            result,
            {
                self.USER_OID: self.LINE_NAME
            }
        )

    def test_get_batch_user_name_all_user_not_exists(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4])

        result = IdentitySearcher.get_batch_user_name([self.USER_OID, self.USER_OID_2], self.CHANNEL_4)
        self.assertEqual(result, {})

    def test_get_batch_user_name_on_not_found_specified(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4])
        RootUserManager.insert_many([
            RootUserModel(Id=self.USER_OID, ApiOid=self.API_OID, Config=RootUserConfigModel.generate_default()),
            RootUserModel(Id=self.USER_OID_2, ApiOid=self.API_OID_2, Config=RootUserConfigModel.generate_default())
        ])
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        )

        result = IdentitySearcher.get_batch_user_name([self.USER_OID, self.USER_OID_2], self.CHANNEL_4,
                                                      on_not_found="N/A")
        self.assertEqual(
            result,
            {
                self.USER_OID: "N/A",
                self.USER_OID_2: "N/A"
            }
        )

    def test_get_batch_user_name_user_missed(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4])
        RootUserManager.insert_many([
            RootUserModel(Id=self.USER_OID, OnPlatOids=[self.ONPLAT_OID],
                          Config=RootUserConfigModel.generate_default())
        ])
        OnPlatformIdentityManager.insert_one(
            OnPlatformUserModel(Id=self.ONPLAT_OID, Platform=Platform.LINE, Token=self.LINE_TOKEN)
        )

        result = IdentitySearcher.get_batch_user_name([self.USER_OID_2], self.CHANNEL_4,
                                                      on_not_found="N/A")
        self.assertEqual(result, {})

    def test_get_batch_user_name_no_data(self):
        result = IdentitySearcher.get_batch_user_name([self.USER_OID, self.USER_OID_2], self.CHANNEL_4)
        self.assertEqual(result, {})
