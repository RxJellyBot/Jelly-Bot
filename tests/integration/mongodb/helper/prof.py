from bson import ObjectId

from extutils.gidentity import GoogleIdentityUserData
from flags import Platform, PermissionLevel, ProfilePermission
from models import ChannelModel, ChannelConfigModel, ChannelProfileModel, ChannelProfileConnectionModel
from mongodb.factory import ChannelManager, RootUserManager
from mongodb.factory.prof_base import ProfileDataManager, UserProfileManager
from mongodb.helper import ProfileHelper
from tests.base import TestCase

__all__ = ("TestProfileHelper",)


class TestProfileHelper(TestCase):
    PROF_DEFAULT_OID = ObjectId()
    PROF_1_OID = ObjectId()
    PROF_2_OID = ObjectId()
    PROF_3_OID = ObjectId()
    PROF_4_OID = ObjectId()
    CHANNEL_OID = ObjectId()

    PROFILE_DEFAULT = ChannelProfileModel(Id=PROF_DEFAULT_OID, ChannelOid=CHANNEL_OID, Name="Default")
    PROFILE_1 = ChannelProfileModel(Id=PROF_1_OID, ChannelOid=CHANNEL_OID, Name="Profile 1",
                                    PermissionLevel=PermissionLevel.MOD)
    PROFILE_2 = ChannelProfileModel(Id=PROF_2_OID, ChannelOid=CHANNEL_OID, Name="Profile 2",
                                    Permission={ProfilePermission.PRF_CONTROL_SELF.code_str: True})
    PROFILE_3 = ChannelProfileModel(Id=PROF_3_OID, ChannelOid=CHANNEL_OID, Name="Profile 3",
                                    Permission={ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
    PROFILE_4 = ChannelProfileModel(Id=PROF_4_OID, ChannelOid=CHANNEL_OID, Name="Profile 4")
    CHANNEL = ChannelModel(
        Id=CHANNEL_OID, Platform=Platform.LINE, Token="C123456",
        Config=ChannelConfigModel.generate_default(DefaultProfileOid=PROF_DEFAULT_OID)
    )

    @staticmethod
    def obj_to_clear():
        return [RootUserManager, ChannelManager, ProfileDataManager, UserProfileManager]

    @classmethod
    def _setup_prof_controls(cls):
        # Not registering on-plat because it causes user to be marked unavailable, yielding incorrect result
        goo_1 = GoogleIdentityUserData("FakeAUD", "FakeISS", "FakeUID1", "Fake1@email.com", skip_check=True)
        goo_2 = GoogleIdentityUserData("FakeAUD", "FakeISS", "FakeUID2", "Fake2@email.com", skip_check=True)
        goo_3 = GoogleIdentityUserData("FakeAUD", "FakeISS", "FakeUID3", "Fake3@email.com", skip_check=True)
        goo_4 = GoogleIdentityUserData("FakeAUD", "FakeISS", "FakeUID4", "Fake4@email.com", skip_check=True)

        uid1 = RootUserManager.register_google(goo_1).model.id
        uid2 = RootUserManager.register_google(goo_2).model.id
        uid3 = RootUserManager.register_google(goo_3).model.id
        uid4 = RootUserManager.register_google(goo_4).model.id

        return uid1, uid2, uid3, uid4

    def test_get_user_profile_controls_control_self(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_2_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_2_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_2_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_user_profile_controls(
            self.CHANNEL, self.PROF_4_OID, uid1,
            {ProfilePermission.NORMAL, ProfilePermission.PRF_CONTROL_SELF}
        )
        self.assertEqual(len(result), 3)
        entry = result[0]
        self.assertEqual(entry.root_oid, uid1)
        self.assertEqual(entry.name, f"UID - {uid1}")
        self.assertTrue(entry.controllable)
        entry = result[1]
        self.assertEqual(entry.root_oid, uid2)
        self.assertEqual(entry.name, f"UID - {uid2}")
        self.assertFalse(entry.controllable)
        entry = result[2]
        self.assertEqual(entry.root_oid, uid4)
        self.assertEqual(entry.name, f"UID - {uid4}")
        self.assertFalse(entry.controllable)

    def test_get_user_profile_controls_control_member(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_2_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_user_profile_controls(
            self.CHANNEL, self.PROF_4_OID, uid1,
            {ProfilePermission.NORMAL, ProfilePermission.PRF_CONTROL_MEMBER}
        )
        self.assertEqual(len(result), 4)
        entry = result[0]
        self.assertEqual(entry.root_oid, uid1)
        self.assertEqual(entry.name, f"UID - {uid1}")
        self.assertFalse(entry.controllable)
        entry = result[1]
        self.assertEqual(entry.root_oid, uid2)
        self.assertEqual(entry.name, f"UID - {uid2}")
        self.assertTrue(entry.controllable)
        entry = result[2]
        self.assertEqual(entry.root_oid, uid3)
        self.assertEqual(entry.name, f"UID - {uid3}")
        self.assertTrue(entry.controllable)
        entry = result[3]
        self.assertEqual(entry.root_oid, uid4)
        self.assertEqual(entry.name, f"UID - {uid4}")
        self.assertTrue(entry.controllable)

    def test_get_user_profile_controls_no_control(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_2_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_user_profile_controls(
            self.CHANNEL, self.PROF_4_OID, uid1, {ProfilePermission.NORMAL}
        )
        self.assertEqual(len(result), 3)
        entry = result[0]
        self.assertEqual(entry.root_oid, uid2)
        self.assertEqual(entry.name, f"UID - {uid2}")
        self.assertFalse(entry.controllable)
        entry = result[1]
        self.assertEqual(entry.root_oid, uid3)
        self.assertEqual(entry.name, f"UID - {uid3}")
        self.assertFalse(entry.controllable)
        entry = result[2]
        self.assertEqual(entry.root_oid, uid4)
        self.assertEqual(entry.name, f"UID - {uid4}")
        self.assertFalse(entry.controllable)

    def test_get_user_profile_controls_no_member(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        result = ProfileHelper.get_user_profile_controls(
            self.CHANNEL, self.PROF_4_OID, uid1,
            {ProfilePermission.NORMAL, ProfilePermission.PRF_CONTROL_MEMBER}
        )
        self.assertEqual(len(result), 0)

    def test_get_user_profile_controls_on_default(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_2_OID, self.PROF_3_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_2_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_user_profile_controls(
            self.CHANNEL, self.PROF_DEFAULT_OID, uid1, {ProfilePermission.NORMAL}
        )
        self.assertEqual(len(result), 4)
        entry = result[0]
        self.assertEqual(entry.root_oid, uid1)
        self.assertEqual(entry.name, f"UID - {uid1}")
        self.assertFalse(entry.controllable)
        entry = result[1]
        self.assertEqual(entry.root_oid, uid2)
        self.assertEqual(entry.name, f"UID - {uid2}")
        self.assertFalse(entry.controllable)
        entry = result[2]
        self.assertEqual(entry.root_oid, uid3)
        self.assertEqual(entry.name, f"UID - {uid3}")
        self.assertFalse(entry.controllable)
        entry = result[3]
        self.assertEqual(entry.root_oid, uid4)
        self.assertEqual(entry.name, f"UID - {uid4}")
        self.assertFalse(entry.controllable)

    def test_get_user_profile_controls_on_higher_lv(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_2_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_user_profile_controls(
            self.CHANNEL, self.PROF_1_OID, uid1, {ProfilePermission.NORMAL, ProfilePermission.PRF_CONTROL_MEMBER}
        )
        self.assertEqual(len(result), 3)
        entry = result[0]
        self.assertEqual(entry.root_oid, uid2)
        self.assertEqual(entry.name, f"UID - {uid2}")
        self.assertFalse(entry.controllable)
        entry = result[1]
        self.assertEqual(entry.root_oid, uid3)
        self.assertEqual(entry.name, f"UID - {uid3}")
        self.assertFalse(entry.controllable)
        entry = result[2]
        self.assertEqual(entry.root_oid, uid4)
        self.assertEqual(entry.name, f"UID - {uid4}")
        self.assertFalse(entry.controllable)

    def test_get_channel_profiles_no_partial_name(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_2_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_channel_profiles(self.CHANNEL_OID)
        self.assertEqual(len(result), 5)
        entry = result[0]
        self.assertEqual(entry.profile, self.PROFILE_DEFAULT)
        self.assertEqual(entry.owner_names, [f"UID - {uid1}", f"UID - {uid2}", f"UID - {uid3}", f"UID - {uid4}"])
        entry = result[1]
        self.assertEqual(entry.profile, self.PROFILE_1)
        self.assertEqual(entry.owner_names, [f"UID - {uid2}", f"UID - {uid3}", f"UID - {uid4}"])
        entry = result[2]
        self.assertEqual(entry.profile, self.PROFILE_2)
        self.assertEqual(entry.owner_names, [f"UID - {uid2}"])
        entry = result[3]
        self.assertEqual(entry.profile, self.PROFILE_3)
        self.assertEqual(entry.owner_names, [f"UID - {uid1}", f"UID - {uid3}", f"UID - {uid4}"])
        entry = result[4]
        self.assertEqual(entry.profile, self.PROFILE_4)
        self.assertEqual(entry.owner_names, [f"UID - {uid2}", f"UID - {uid3}", f"UID - {uid4}"])

    def test_get_channel_profiles_partial_name(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_2_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_channel_profiles(self.CHANNEL_OID, "Profile ")
        self.assertEqual(len(result), 4)
        entry = result[0]
        self.assertEqual(entry.profile, self.PROFILE_1)
        self.assertEqual(entry.owner_names, [f"UID - {uid2}", f"UID - {uid3}", f"UID - {uid4}"])
        entry = result[1]
        self.assertEqual(entry.profile, self.PROFILE_2)
        self.assertEqual(entry.owner_names, [f"UID - {uid2}"])
        entry = result[2]
        self.assertEqual(entry.profile, self.PROFILE_3)
        self.assertEqual(entry.owner_names, [f"UID - {uid1}", f"UID - {uid3}", f"UID - {uid4}"])
        entry = result[3]
        self.assertEqual(entry.profile, self.PROFILE_4)
        self.assertEqual(entry.owner_names, [f"UID - {uid2}", f"UID - {uid3}", f"UID - {uid4}"])

    def test_get_channel_profiles_full_name(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_2_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_channel_profiles(self.CHANNEL_OID, "Profile 1")
        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry.profile, self.PROFILE_1)
        self.assertEqual(entry.owner_names, [f"UID - {uid2}", f"UID - {uid3}", f"UID - {uid4}"])

    def test_get_channel_profiles_channel_not_exists(self):
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        uid1, uid2, uid3, uid4 = self._setup_prof_controls()

        UserProfileManager.insert_many(
            [
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid1,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_3_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid2,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_2_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid3,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                ),
                ChannelProfileConnectionModel(
                    ChannelOid=self.CHANNEL_OID, UserOid=uid4,
                    ProfileOids=[self.PROF_DEFAULT_OID, self.PROF_1_OID, self.PROF_3_OID, self.PROF_4_OID]
                )
            ]
        )

        result = ProfileHelper.get_channel_profiles(self.CHANNEL_OID, "Profile 1")
        self.assertEqual(len(result), 0)

    def test_get_channel_profiles_channel_no_prof(self):
        ChannelManager.insert_one(self.CHANNEL)
        self._setup_prof_controls()

        result = ProfileHelper.get_channel_profiles(self.CHANNEL_OID, "Profile ")
        self.assertEqual(len(result), 0)

    def test_get_channel_profiles_channel_no_prof_conn(self):
        ChannelManager.insert_one(self.CHANNEL)
        ProfileDataManager.insert_many([self.PROFILE_DEFAULT, self.PROFILE_1, self.PROFILE_2,
                                        self.PROFILE_3, self.PROFILE_4])
        self._setup_prof_controls()

        result = ProfileHelper.get_channel_profiles(self.CHANNEL_OID, "Profile ")
        self.assertEqual(len(result), 4)
        entry = result[0]
        self.assertEqual(entry.profile, self.PROFILE_1)
        self.assertEqual(entry.owner_names, [])
        entry = result[1]
        self.assertEqual(entry.profile, self.PROFILE_2)
        self.assertEqual(entry.owner_names, [])
        entry = result[2]
        self.assertEqual(entry.profile, self.PROFILE_3)
        self.assertEqual(entry.owner_names, [])
        entry = result[3]
        self.assertEqual(entry.profile, self.PROFILE_4)
        self.assertEqual(entry.owner_names, [])
