from datetime import datetime

from bson import ObjectId
from django.conf import settings

from extutils.emailutils import EmailServer
from flags import Platform, MessageType
from models import ChannelModel, ChannelConfigModel, MessageRecordModel, ChannelProfileConnectionModel
from mongodb.factory import ChannelManager, ProfileManager, RootUserManager, MessageRecordStatisticsManager
from mongodb.factory.prof import UserProfileManager
from mongodb.helper import InfoProcessor
from tests.base import TestCase

__all__ = ("TestInfoProcessor",)


class TestInfoProcessor(TestCase):
    USER_1_OID = ObjectId()

    CHANNEL_1_OID = ObjectId()
    CHANNEL_2_OID = ObjectId()
    CHANNEL_3_OID = ObjectId()
    CHANNEL_4_OID = ObjectId()
    CHANNEL_5_OID = ObjectId()

    PROF_OID = ObjectId()

    CHANNEL_1 = ChannelModel(Id=CHANNEL_1_OID, Platform=Platform.LINE, Token="CHANNEL1",
                             Config=ChannelConfigModel.generate_default(DefaultProfileOid=PROF_OID),
                             Name={str(USER_1_OID): "CUST_NAME"})
    CHANNEL_2 = ChannelModel(Id=CHANNEL_2_OID, Platform=Platform.LINE, Token="CHANNEL2",
                             Config=ChannelConfigModel.generate_default(DefaultProfileOid=ObjectId()))
    CHANNEL_3 = ChannelModel(Id=CHANNEL_3_OID, Platform=Platform.LINE, Token="CHANNEL3",
                             Config=ChannelConfigModel.generate_default(DefaultProfileOid=ObjectId()))
    CHANNEL_4 = ChannelModel(Id=CHANNEL_4_OID, Platform=Platform.LINE, Token="CHANNEL4",
                             Config=ChannelConfigModel.generate_default(DefaultProfileOid=ObjectId()),
                             BotAccessible=False)
    CHANNEL_5 = ChannelModel(Id=CHANNEL_5_OID, Platform=Platform.LINE, Token="CHANNEL5",
                             Config=ChannelConfigModel.generate_default(DefaultProfileOid=ObjectId()))

    @staticmethod
    def obj_to_clear():
        return [ChannelManager, ProfileManager, RootUserManager, MessageRecordStatisticsManager, EmailServer]

    def test_collate_child_channel_data(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4, self.CHANNEL_5])

        channel_data = InfoProcessor.collate_child_channel_data(
            self.USER_1_OID,
            [self.CHANNEL_1_OID, self.CHANNEL_2_OID, self.CHANNEL_3_OID, self.CHANNEL_4_OID, self.CHANNEL_5_OID]
        )
        self.assertEqual(len(channel_data), 5)
        self.assertEqual(channel_data[0].channel_data, self.CHANNEL_5)
        self.assertEqual(channel_data[0].channel_name, "CHANNEL5")
        self.assertEqual(channel_data[1].channel_data, self.CHANNEL_3)
        self.assertEqual(channel_data[1].channel_name, "CHANNEL3")
        self.assertEqual(channel_data[2].channel_data, self.CHANNEL_2)
        self.assertEqual(channel_data[2].channel_name, "CHANNEL2")
        self.assertEqual(channel_data[3].channel_data, self.CHANNEL_1)
        self.assertEqual(channel_data[3].channel_name, "CUST_NAME")
        self.assertEqual(channel_data[4].channel_data, self.CHANNEL_4)
        self.assertEqual(channel_data[4].channel_name, "CHANNEL4")

        self.assertEqual(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)

    def test_collate_child_channel_data_partial_missed(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4, self.CHANNEL_5])

        channel_data = InfoProcessor.collate_child_channel_data(
            self.USER_1_OID,
            [self.CHANNEL_1_OID, self.CHANNEL_2_OID, self.CHANNEL_3_OID, self.CHANNEL_4_OID, ObjectId()]
        )
        self.assertEqual(len(channel_data), 4)
        self.assertEqual(channel_data[0].channel_data, self.CHANNEL_3)
        self.assertEqual(channel_data[0].channel_name, "CHANNEL3")
        self.assertEqual(channel_data[1].channel_data, self.CHANNEL_2)
        self.assertEqual(channel_data[1].channel_name, "CHANNEL2")
        self.assertEqual(channel_data[2].channel_data, self.CHANNEL_1)
        self.assertEqual(channel_data[2].channel_name, "CUST_NAME")
        self.assertEqual(channel_data[3].channel_data, self.CHANNEL_4)
        self.assertEqual(channel_data[3].channel_name, "CHANNEL4")

        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)

    def test_collate_child_channel_no_child(self):
        ChannelManager.insert_many([self.CHANNEL_1, self.CHANNEL_2, self.CHANNEL_3, self.CHANNEL_4, self.CHANNEL_5])

        channel_data = InfoProcessor.collate_child_channel_data(self.USER_1_OID, [])
        self.assertEqual(len(channel_data), 0)
        self.assertEqual(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)

    def test_collate_child_channel_no_data(self):
        channel_data = InfoProcessor.collate_child_channel_data(
            self.USER_1_OID,
            [self.CHANNEL_1_OID, self.CHANNEL_2_OID, self.CHANNEL_3_OID, self.CHANNEL_4_OID, self.CHANNEL_5_OID]
        )
        self.assertEqual(len(channel_data), 0)
        self.assertGreater(len(EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails), 0)

    def test_get_member_info(self):
        ChannelManager.insert_one(self.CHANNEL_1)

        ProfileManager.create_default_profile(self.CHANNEL_1_OID)
        root_1_mdl = RootUserManager.register_onplat(Platform.LINE, "USER1").model
        ProfileManager.register_new_default(self.CHANNEL_1_OID, root_1_mdl.id)
        root_2_mdl = RootUserManager.register_onplat(Platform.LINE, "USER2").model
        ProfileManager.register_new_default(self.CHANNEL_1_OID, root_2_mdl.id)

        join_time_1 = UserProfileManager.find_one_casted({
            ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_1_OID,
            ChannelProfileConnectionModel.UserOid.key: root_1_mdl.id
        }, parse_cls=ChannelProfileConnectionModel).id.generation_time
        join_time_2 = UserProfileManager.find_one_casted({
            ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_1_OID,
            ChannelProfileConnectionModel.UserOid.key: root_2_mdl.id
        }, parse_cls=ChannelProfileConnectionModel).id.generation_time

        MessageRecordStatisticsManager.insert_one_model(
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 8, 20)),
                               ChannelOid=self.CHANNEL_1_OID, UserRootOid=root_1_mdl.id,
                               MessageType=MessageType.TEXT, MessageContent="CONTENT")
        )
        MessageRecordStatisticsManager.insert_one_model(
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 8, 19)),
                               ChannelOid=self.CHANNEL_1_OID, UserRootOid=root_2_mdl.id,
                               MessageType=MessageType.TEXT, MessageContent="CONTENT2")
        )

        result = InfoProcessor.get_member_info(self.CHANNEL_1)

        self.assertEqual(len(result), 2)
        result_entry = result[0]
        self.assertEqual(result_entry.user_oid, root_1_mdl.id)
        self.assertEqual(result_entry.user_name, "USER1 (LINE)")
        self.assertEqual(result_entry.first_joined_str, join_time_1.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result_entry.last_message_at_str, "2020-08-20 00:00:00")
        result_entry = result[1]
        self.assertEqual(result_entry.user_oid, root_2_mdl.id)
        self.assertEqual(result_entry.user_name, "USER2 (LINE)")
        self.assertEqual(result_entry.first_joined_str, join_time_2.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result_entry.last_message_at_str, "2020-08-19 00:00:00")

    def test_get_member_info_partial_no_last_message(self):
        ChannelManager.insert_one(self.CHANNEL_1)

        ProfileManager.create_default_profile(self.CHANNEL_1_OID)
        root_1_mdl = RootUserManager.register_onplat(Platform.LINE, "USER1").model
        ProfileManager.register_new_default(self.CHANNEL_1_OID, root_1_mdl.id)
        root_2_mdl = RootUserManager.register_onplat(Platform.LINE, "USER2").model
        ProfileManager.register_new_default(self.CHANNEL_1_OID, root_2_mdl.id)

        join_time_1 = UserProfileManager.find_one_casted({
            ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_1_OID,
            ChannelProfileConnectionModel.UserOid.key: root_1_mdl.id
        }, parse_cls=ChannelProfileConnectionModel).id.generation_time
        join_time_2 = UserProfileManager.find_one_casted({
            ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_1_OID,
            ChannelProfileConnectionModel.UserOid.key: root_2_mdl.id
        }, parse_cls=ChannelProfileConnectionModel).id.generation_time

        MessageRecordStatisticsManager.insert_one_model(
            MessageRecordModel(Id=ObjectId.from_datetime(datetime(2020, 8, 19)),
                               ChannelOid=self.CHANNEL_1_OID, UserRootOid=root_2_mdl.id,
                               MessageType=MessageType.TEXT, MessageContent="CONTENT2")
        )

        result = InfoProcessor.get_member_info(self.CHANNEL_1)

        self.assertEqual(len(result), 2)
        result_entry = result[0]
        self.assertEqual(result_entry.user_oid, root_1_mdl.id)
        self.assertEqual(result_entry.user_name, "USER1 (LINE)")
        self.assertEqual(result_entry.first_joined_str, join_time_1.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result_entry.last_message_at_str, "N/A")
        result_entry = result[1]
        self.assertEqual(result_entry.user_oid, root_2_mdl.id)
        self.assertEqual(result_entry.user_name, "USER2 (LINE)")
        self.assertEqual(result_entry.first_joined_str, join_time_2.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result_entry.last_message_at_str, "2020-08-19 00:00:00")

    def test_get_member_info_no_last_message(self):
        ChannelManager.insert_one(self.CHANNEL_1)

        ProfileManager.create_default_profile(self.CHANNEL_1_OID)
        root_1_mdl = RootUserManager.register_onplat(Platform.LINE, "USER1").model
        ProfileManager.register_new_default(self.CHANNEL_1_OID, root_1_mdl.id)
        root_2_mdl = RootUserManager.register_onplat(Platform.LINE, "USER2").model
        ProfileManager.register_new_default(self.CHANNEL_1_OID, root_2_mdl.id)

        join_time_1 = UserProfileManager.find_one_casted({
            ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_1_OID,
            ChannelProfileConnectionModel.UserOid.key: root_1_mdl.id
        }, parse_cls=ChannelProfileConnectionModel).id.generation_time
        join_time_2 = UserProfileManager.find_one_casted({
            ChannelProfileConnectionModel.ChannelOid.key: self.CHANNEL_1_OID,
            ChannelProfileConnectionModel.UserOid.key: root_2_mdl.id
        }, parse_cls=ChannelProfileConnectionModel).id.generation_time

        result = InfoProcessor.get_member_info(self.CHANNEL_1)

        self.assertEqual(len(result), 2)
        result_entry = result[0]
        self.assertEqual(result_entry.user_oid, root_1_mdl.id)
        self.assertEqual(result_entry.user_name, "USER1 (LINE)")
        self.assertEqual(result_entry.first_joined_str, join_time_1.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result_entry.last_message_at_str, "N/A")
        result_entry = result[1]
        self.assertEqual(result_entry.user_oid, root_2_mdl.id)
        self.assertEqual(result_entry.user_name, "USER2 (LINE)")
        self.assertEqual(result_entry.first_joined_str, join_time_2.strftime("%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result_entry.last_message_at_str, "N/A")

    def test_get_member_info_no_member(self):
        ChannelManager.insert_one(self.CHANNEL_1)

        result = InfoProcessor.get_member_info(self.CHANNEL_1)

        self.assertEqual(len(result), 0)
