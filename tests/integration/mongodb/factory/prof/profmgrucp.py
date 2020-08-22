from bson import ObjectId
from django.conf import settings

from extutils.emailutils import EmailServer
from flags import Platform, ProfilePermission
from models import ChannelModel, ChannelProfileModel, ChannelConfigModel, ChannelProfileConnectionModel
from mongodb.factory import ChannelManager, ProfileManager
from mongodb.factory.prof_base import ProfileDataManager, UserProfileManager
from strres.mongodb import Profile
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestProfileManagerUserChannelProfile", "TestProfileManagerUserChannelProfileEmpty",
           "TestProfileManagerUserChannelProfileDangling"]


class TestProfileManagerUserChannelProfile(TestModelMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()
    CHANNEL_OID_3 = ObjectId()
    CHANNEL_OID_4 = ObjectId()

    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()
    USER_OID_3 = ObjectId()

    PROF = None
    PROF_2 = None
    PROF_3 = None
    PROF_4 = None
    PROF_5 = None

    CHANNEL = None
    CHANNEL_2 = None
    CHANNEL_3 = None
    CHANNEL_4 = None

    @staticmethod
    def obj_to_clear():
        return [ProfileManager]

    def setUpTestCase(self) -> None:
        ChannelManager.clear()

        self.PROF = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                        Permission={ProfilePermission.PRF_CED.code_str: True})
        self.PROF_2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        self.PROF_3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        self.PROF_4 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_3, Name="JKL")
        self.PROF_5 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_4, Name="MNO")
        ProfileDataManager.insert_one_model(self.PROF)
        ProfileDataManager.insert_one_model(self.PROF_2)
        ProfileDataManager.insert_one_model(self.PROF_3)
        ProfileDataManager.insert_one_model(self.PROF_4)
        ProfileDataManager.insert_one_model(self.PROF_5)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF.id, self.PROF_2.id])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_2.id], Starred=True)
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_3,
                                          ProfileOids=[])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_3.id], Starred=True)
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_3.id])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_3, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_4, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_5.id])
        )
        self.CHANNEL = ChannelModel(Id=self.CHANNEL_OID, Platform=Platform.LINE, Token="C1",
                                    Config=ChannelConfigModel.generate_default(
                                        DefaultProfileOid=self.PROF_2.id, DefaultName="DCNL"),
                                    Name={str(self.USER_OID): "CNL"})
        self.CHANNEL_2 = ChannelModel(Id=self.CHANNEL_OID_2, Platform=Platform.LINE, Token="C2",
                                      Config=ChannelConfigModel.generate_default(
                                          DefaultProfileOid=self.PROF_3.id, DefaultName="DCNL2"))
        self.CHANNEL_3 = ChannelModel(Id=self.CHANNEL_OID_3, Platform=Platform.LINE, Token="C3",
                                      Config=ChannelConfigModel.generate_default(
                                          DefaultProfileOid=self.PROF_4.id, DefaultName="DCNL3"))
        self.CHANNEL_4 = ChannelModel(Id=self.CHANNEL_OID_4, Platform=Platform.LINE, Token="C4",
                                      BotAccessible=False,
                                      Config=ChannelConfigModel.generate_default(
                                          DefaultProfileOid=self.PROF_5.id, DefaultName="DCNL4"))
        ChannelManager.insert_one_model(self.CHANNEL)
        ChannelManager.insert_one_model(self.CHANNEL_2)
        ChannelManager.insert_one_model(self.CHANNEL_3)
        ChannelManager.insert_one_model(self.CHANNEL_4)

    def test_get_profs(self):
        profs = ProfileManager.get_user_channel_profiles(self.USER_OID)

        self.assertEqual(len(profs), 2)

        obj = profs[0]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_2, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL2")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_3])
        self.assertEqual(obj.starred, True)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_3.id)

        obj = profs[1]
        self.assertModelEqual(obj.channel_data, self.CHANNEL, ignore_oid=False)
        self.assertEqual(obj.channel_name, "CNL")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF, self.PROF_2])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, True)
        self.assertEqual(obj.default_profile_oid, self.PROF_2.id)

        profs = ProfileManager.get_user_channel_profiles(self.USER_OID_2)

        self.assertEqual(len(profs), 2)

        obj = profs[0]
        self.assertModelEqual(obj.channel_data, self.CHANNEL, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_2])
        self.assertEqual(obj.starred, True)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_2.id)

        obj = profs[1]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_2, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL2")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_3])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_3.id)

    def test_get_profs_not_inside_only(self):
        profs = ProfileManager.get_user_channel_profiles(self.USER_OID, inside_only=False)

        self.assertEqual(len(profs), 3)

        obj = profs[0]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_2, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL2")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_3])
        self.assertEqual(obj.starred, True)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_3.id)

        obj = profs[1]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_3, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL3")
        self.assertModelSequenceEqual(obj.profiles, [])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_4.id)

        obj = profs[2]
        self.assertModelEqual(obj.channel_data, self.CHANNEL, ignore_oid=False)
        self.assertEqual(obj.channel_name, "CNL")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF, self.PROF_2])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, True)
        self.assertEqual(obj.default_profile_oid, self.PROF_2.id)

    def test_get_profs_not_accessible_only(self):
        profs = ProfileManager.get_user_channel_profiles(self.USER_OID, accessbible_only=False)

        self.assertEqual(len(profs), 3)

        obj = profs[0]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_2, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL2")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_3])
        self.assertEqual(obj.starred, True)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_3.id)

        obj = profs[1]
        self.assertModelEqual(obj.channel_data, self.CHANNEL, ignore_oid=False)
        self.assertEqual(obj.channel_name, "CNL")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF, self.PROF_2])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, True)
        self.assertEqual(obj.default_profile_oid, self.PROF_2.id)

        obj = profs[2]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_4, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL4")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_5])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_5.id)

    def test_get_profs_not_inside_accessible_only(self):
        profs = ProfileManager.get_user_channel_profiles(self.USER_OID, inside_only=False, accessbible_only=False)

        self.assertEqual(len(profs), 4)

        obj = profs[0]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_2, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL2")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_3])
        self.assertEqual(obj.starred, True)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_3.id)

        obj = profs[1]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_3, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL3")
        self.assertModelSequenceEqual(obj.profiles, [])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_4.id)

        obj = profs[2]
        self.assertModelEqual(obj.channel_data, self.CHANNEL, ignore_oid=False)
        self.assertEqual(obj.channel_name, "CNL")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF, self.PROF_2])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, True)
        self.assertEqual(obj.default_profile_oid, self.PROF_2.id)

        obj = profs[3]
        self.assertModelEqual(obj.channel_data, self.CHANNEL_4, ignore_oid=False)
        self.assertEqual(obj.channel_name, "DCNL4")
        self.assertModelSequenceEqual(obj.profiles, [self.PROF_5])
        self.assertEqual(obj.starred, False)
        self.assertEqual(obj.can_ced_profile, False)
        self.assertEqual(obj.default_profile_oid, self.PROF_5.id)

    def test_get_profs_user_miss(self):
        profs = ProfileManager.get_user_channel_profiles(ObjectId(), inside_only=False, accessbible_only=False)

        self.assertEqual(len(profs), 0)


class TestProfileManagerUserChannelProfileEmpty(TestDatabaseMixin):
    @staticmethod
    def obj_to_clear():
        return [ProfileManager, ChannelManager]

    def test_get_profs_no_data(self):
        profs = ProfileManager.get_user_channel_profiles(TestProfileManagerUserChannelProfile.USER_OID,
                                                         inside_only=False, accessbible_only=False)
        self.assertEqual(len(profs), 0)

        profs = ProfileManager.get_user_channel_profiles(TestProfileManagerUserChannelProfile.USER_OID,
                                                         inside_only=False)
        self.assertEqual(len(profs), 0)

        profs = ProfileManager.get_user_channel_profiles(TestProfileManagerUserChannelProfile.USER_OID,
                                                         accessbible_only=False)
        self.assertEqual(len(profs), 0)

        profs = ProfileManager.get_user_channel_profiles(TestProfileManagerUserChannelProfile.USER_OID)
        self.assertEqual(len(profs), 0)


class TestProfileManagerUserChannelProfileDangling(TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()
    CHANNEL_OID_3 = ObjectId()
    CHANNEL_OID_4 = ObjectId()

    USER_OID = ObjectId()

    PROFILE_OID = ObjectId()
    PROFILE_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [ProfileManager, ChannelManager]

    def test_get_profs_dangling_channel(self):
        prof = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        prof_2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        prof_3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        prof_4 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_3, Name="JKL")
        prof_5 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_4, Name="MNO")
        ProfileDataManager.insert_one_model(prof)
        ProfileDataManager.insert_one_model(prof_2)
        ProfileDataManager.insert_one_model(prof_3)
        ProfileDataManager.insert_one_model(prof_4)
        ProfileDataManager.insert_one_model(prof_5)
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[prof.id, prof_2.id])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[prof_3.id], Starred=True)
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_3, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_4, UserOid=self.USER_OID,
                                          ProfileOids=[prof_5.id])
        )
        channel_2 = ChannelModel(Id=self.CHANNEL_OID_2, Platform=Platform.LINE, Token="U7890AB",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_3.id, DefaultName="DCNL2"))
        channel_3 = ChannelModel(Id=self.CHANNEL_OID_3, Platform=Platform.LINE, Token="UCDEF01",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_4.id, DefaultName="DCNL3"))
        channel_4 = ChannelModel(Id=self.CHANNEL_OID_4, Platform=Platform.LINE, Token="U234567",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_5.id, DefaultName="DCNL4"))
        ChannelManager.insert_one_model(channel_2)
        ChannelManager.insert_one_model(channel_3)
        ChannelManager.insert_one_model(channel_4)

        ProfileManager.get_user_channel_profiles(self.USER_OID)

        mail = EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails.pop()
        self.assertIsNotNone(mail)
        self.assertTrue(Profile.DANGLING_PROF_CONN_DATA in mail.subject)
        self.assertEqual(mail.content, Profile.dangling_content({mdl.id: self.CHANNEL_OID}))

    def test_get_profs_dangling_profile(self):
        prof = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        prof_2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        prof_3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        prof_4 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_3, Name="JKL")
        prof_5 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_4, Name="MNO")
        ProfileDataManager.insert_one_model(prof)
        ProfileDataManager.insert_one_model(prof_2)
        ProfileDataManager.insert_one_model(prof_3)
        ProfileDataManager.insert_one_model(prof_4)
        ProfileDataManager.insert_one_model(prof_5)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[prof.id, prof_2.id]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[prof_3.id], Starred=True)
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_3, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_4, UserOid=self.USER_OID,
                                            ProfileOids=[self.PROFILE_OID, self.PROFILE_OID_2])
        UserProfileManager.insert_one_model(mdl)
        channel = ChannelModel(Id=self.CHANNEL_OID, Platform=Platform.LINE, Token="U123456",
                               Config=ChannelConfigModel.generate_default(
                                   DefaultProfileOid=prof_2.id, DefaultName="DCNL"),
                               Name={str(self.USER_OID): "CNL"})
        channel_2 = ChannelModel(Id=self.CHANNEL_OID_2, Platform=Platform.LINE, Token="U7890AB",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_3.id, DefaultName="DCNL2"))
        channel_3 = ChannelModel(Id=self.CHANNEL_OID_3, Platform=Platform.LINE, Token="UCDEF01",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_4.id, DefaultName="DCNL3"))
        channel_4 = ChannelModel(Id=self.CHANNEL_OID_4, Platform=Platform.LINE, Token="U234567",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_5.id, DefaultName="DCNL4"))
        ChannelManager.insert_one_model(channel)
        ChannelManager.insert_one_model(channel_2)
        ChannelManager.insert_one_model(channel_3)
        ChannelManager.insert_one_model(channel_4)

        ProfileManager.get_user_channel_profiles(self.USER_OID)

        mail = EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails.pop()
        self.assertIsNotNone(mail)
        self.assertTrue(Profile.DANGLING_PROF_CONN_DATA in mail.subject)
        self.assertEqual(mail.content, Profile.dangling_content({mdl.id: [self.PROFILE_OID, self.PROFILE_OID_2]}))

    def test_get_profs_dangling_channel_profile(self):
        prof = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        prof_2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        prof_3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        prof_4 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_3, Name="JKL")
        prof_5 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_4, Name="MNO")
        ProfileDataManager.insert_one_model(prof)
        ProfileDataManager.insert_one_model(prof_2)
        ProfileDataManager.insert_one_model(prof_3)
        ProfileDataManager.insert_one_model(prof_4)
        ProfileDataManager.insert_one_model(prof_5)
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[prof.id, prof_2.id])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[prof_3.id], Starred=True)
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_3, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_4, UserOid=self.USER_OID,
                                            ProfileOids=[self.PROFILE_OID, self.PROFILE_OID_2])
        UserProfileManager.insert_one_model(mdl)
        channel = ChannelModel(Id=self.CHANNEL_OID, Platform=Platform.LINE, Token="U123456",
                               Config=ChannelConfigModel.generate_default(
                                   DefaultProfileOid=prof_2.id, DefaultName="DCNL"),
                               Name={str(self.USER_OID): "CNL"})
        channel_2 = ChannelModel(Id=self.CHANNEL_OID_2, Platform=Platform.LINE, Token="U7890AB",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_3.id, DefaultName="DCNL2"))
        channel_3 = ChannelModel(Id=self.CHANNEL_OID_3, Platform=Platform.LINE, Token="UCDEF01",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_4.id, DefaultName="DCNL3"))
        channel_4 = ChannelModel(Id=self.CHANNEL_OID_4, Platform=Platform.LINE, Token="U234567",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_5.id, DefaultName="DCNL4"))
        ChannelManager.insert_one_model(channel)
        ChannelManager.insert_one_model(channel_2)
        ChannelManager.insert_one_model(channel_3)
        ChannelManager.insert_one_model(channel_4)

        ProfileManager.get_user_channel_profiles(self.USER_OID)

        mail = EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails.pop()
        self.assertIsNotNone(mail)
        self.assertTrue(Profile.DANGLING_PROF_CONN_DATA in mail.subject)
        self.assertEqual(mail.content, Profile.dangling_content({mdl.id: [self.PROFILE_OID, self.PROFILE_OID_2]}))

    def test_get_profs_dangling_multi(self):
        prof = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        prof_2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        prof_3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        prof_4 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_3, Name="JKL")
        prof_5 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_4, Name="MNO")
        ProfileDataManager.insert_one_model(prof)
        ProfileDataManager.insert_one_model(prof_2)
        ProfileDataManager.insert_one_model(prof_3)
        ProfileDataManager.insert_one_model(prof_4)
        ProfileDataManager.insert_one_model(prof_5)
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[prof.id, prof_2.id])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[prof_3.id], Starred=True)
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_3, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_4, UserOid=self.USER_OID,
                                             ProfileOids=[self.PROFILE_OID, self.PROFILE_OID_2])
        UserProfileManager.insert_one_model(mdl2)
        channel_2 = ChannelModel(Id=self.CHANNEL_OID_2, Platform=Platform.LINE, Token="U7890AB",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_3.id, DefaultName="DCNL2"))
        channel_3 = ChannelModel(Id=self.CHANNEL_OID_3, Platform=Platform.LINE, Token="UCDEF01",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_4.id, DefaultName="DCNL3"))
        channel_4 = ChannelModel(Id=self.CHANNEL_OID_4, Platform=Platform.LINE, Token="U234567",
                                 Config=ChannelConfigModel.generate_default(
                                     DefaultProfileOid=prof_5.id, DefaultName="DCNL4"))
        ChannelManager.insert_one_model(channel_2)
        ChannelManager.insert_one_model(channel_3)
        ChannelManager.insert_one_model(channel_4)

        ProfileManager.get_user_channel_profiles(self.USER_OID)

        mail = EmailServer.get_mailbox(settings.EMAIL_HOST_USER).mails.pop()
        self.assertIsNotNone(mail)
        self.assertTrue(Profile.DANGLING_PROF_CONN_DATA in mail.subject)
        self.assertEqual(mail.content, Profile.dangling_content({mdl2.id: [self.PROFILE_OID, self.PROFILE_OID_2],
                                                                 mdl.id: self.CHANNEL_OID}))
