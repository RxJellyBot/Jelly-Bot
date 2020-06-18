from bson import ObjectId

from flags import ProfilePermission, PermissionLevel, ProfilePermissionDefault
from models import ChannelProfileModel, ChannelProfileConnectionModel
from mongodb.factory.prof import ProfileManager, ProfileDataManager, UserProfileManager
from tests.base import TestDatabaseMixin, TestModelMixin, TestTimeComparisonMixin

__all__ = ["TestProfileManagerGetInfo"]


class TestProfileManagerGetInfo(TestModelMixin, TestTimeComparisonMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()
    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()
    PROF_OID_1 = ObjectId()
    PROF_OID_2 = ObjectId()

    @staticmethod
    def collections_to_reset():
        return [ProfileManager]

    def test_get_user_prof(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[mdl3.id])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                          ProfileOids=[mdl3.id])
        )

        self.assertModelSetEqual(
            set(ProfileManager.get_user_profiles(self.CHANNEL_OID, self.USER_OID)),
            {mdl, mdl2}
        )
        self.assertModelSetEqual(
            set(ProfileManager.get_user_profiles(self.CHANNEL_OID_2, self.USER_OID)),
            {mdl3}
        )

    def test_get_user_prof_no_user(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[mdl3.id])
        )

        self.assertModelSetEqual(set(ProfileManager.get_user_profiles(self.CHANNEL_OID, self.USER_OID_2)), set())
        self.assertModelSetEqual(set(ProfileManager.get_user_profiles(self.CHANNEL_OID_2, self.USER_OID_2)), set())

    def test_get_user_prof_user_no_prof(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )

        self.assertModelSetEqual(set(ProfileManager.get_user_profiles(self.CHANNEL_OID, self.USER_OID)), set())
        self.assertModelSetEqual(set(ProfileManager.get_user_profiles(self.CHANNEL_OID_2, self.USER_OID)), set())

    def test_get_user_prof_channel_miss(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)

        self.assertModelSetEqual(set(ProfileManager.get_user_profiles(self.CHANNEL_OID, self.USER_OID)), set())

    def test_get_user_prof_no_channel(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )

        self.assertModelSetEqual(set(ProfileManager.get_user_profiles(ObjectId(), self.USER_OID)), set())

    def test_get_channel_prof(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)

        self.assertModelSetEqual(
            set(ProfileManager.get_channel_profiles(self.CHANNEL_OID)),
            {mdl, mdl2}
        )

    def test_get_channel_prof_with_keyword(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="BCD")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)

        self.assertModelSetEqual(
            set(ProfileManager.get_channel_profiles(self.CHANNEL_OID, "AB")),
            {mdl}
        )
        self.assertModelSetEqual(
            set(ProfileManager.get_channel_profiles(self.CHANNEL_OID, "BC")),
            {mdl, mdl2}
        )

    def test_get_channel_prof_channel_miss(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)

        self.assertModelSetEqual(
            set(ProfileManager.get_channel_profiles(ObjectId(), "AB")),
            set()
        )

    def test_get_channel_prof_no_data(self):
        self.assertModelSetEqual(
            set(ProfileManager.get_channel_profiles(self.CHANNEL_OID, "AB")),
            set()
        )
        self.assertModelSetEqual(
            set(ProfileManager.get_channel_profiles(self.CHANNEL_OID)),
            set()
        )

    def test_get_highest_perm_lv(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF", PermissionLevel=PermissionLevel.MOD)
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="GHI", PermissionLevel=PermissionLevel.ADMIN)

        data = (
            ([mdl, mdl2, mdl3], PermissionLevel.ADMIN),
            ([mdl, mdl2], PermissionLevel.MOD),
            ([mdl2, mdl3], PermissionLevel.ADMIN),
            ([mdl, mdl3], PermissionLevel.ADMIN),
            ([mdl], PermissionLevel.lowest()),
            ([mdl2], PermissionLevel.MOD),
            ([mdl3], PermissionLevel.ADMIN),
        )

        for mdls, lv in data:
            with self.subTest(profs=mdls, expected_lv=lv):
                self.assertEqual(ProfileManager.get_highest_permission_level(mdls), lv)

    def test_get_highest_perm_lv_no_prof(self):
        self.assertEqual(ProfileManager.get_highest_permission_level([]), PermissionLevel.lowest())

    def test_get_prof(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)

        self.assertModelEqual(ProfileManager.get_profile(mdl.id), mdl, ignore_oid=False)
        self.assertModelEqual(ProfileManager.get_profile(mdl2.id), mdl2, ignore_oid=False)
        self.assertModelEqual(ProfileManager.get_profile(mdl3.id), mdl3, ignore_oid=False)

    def test_get_prof_no_data(self):
        self.assertIsNone(ProfileManager.get_profile(ObjectId()))

    def test_get_prof_miss(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        ProfileDataManager.insert_one_model(mdl)

        self.assertIsNone(ProfileManager.get_profile(ObjectId()))

    def test_get_prof_name(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        mdl3 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="GHI")
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        ProfileDataManager.insert_one_model(mdl3)

        self.assertModelEqual(ProfileManager.get_profile_name(self.CHANNEL_OID, "ABC"), mdl, ignore_oid=False)
        self.assertModelEqual(ProfileManager.get_profile_name(self.CHANNEL_OID, "DEF"), mdl2, ignore_oid=False)
        self.assertModelEqual(ProfileManager.get_profile_name(self.CHANNEL_OID_2, "GHI"), mdl3, ignore_oid=False)

    def test_prof_name_strip(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="AA ")
        ProfileDataManager.insert_one_model(mdl)

        self.assertEqual(ProfileManager.get_profile_name(self.CHANNEL_OID, " AA "), mdl)
        self.assertEqual(ProfileManager.get_profile_name(self.CHANNEL_OID, "AA "), mdl)

    def test_prof_name_no_data(self):
        self.assertIsNone(ProfileManager.get_profile_name(self.CHANNEL_OID, "ABC"))

    def test_get_prof_name_miss(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        ProfileDataManager.insert_one_model(mdl)

        self.assertIsNone(ProfileManager.get_profile_name(self.CHANNEL_OID, "AB"))
        self.assertIsNone(ProfileManager.get_profile_name(self.CHANNEL_OID_2, "ABC"))

    def test_get_user_channel_dict(self):
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_1]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_OID_2]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_2]))

        self.assertEqual(
            ProfileManager.get_users_exist_channel_dict([self.USER_OID, self.USER_OID_2]),
            {
                self.USER_OID: {self.CHANNEL_OID_2},
                self.USER_OID_2: {self.CHANNEL_OID, self.CHANNEL_OID_2}
            }
        )

    def test_get_user_channel_dict_not_in_any(self):
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_1]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_2]))

        self.assertEqual(
            ProfileManager.get_users_exist_channel_dict([self.USER_OID, self.USER_OID_2]),
            {
                self.USER_OID: set(),
                self.USER_OID_2: {self.CHANNEL_OID, self.CHANNEL_OID_2}
            }
        )

    def test_get_user_channel_dict_no_data(self):
        self.assertEqual(
            ProfileManager.get_users_exist_channel_dict([self.USER_OID, self.USER_OID_2]),
            {}
        )

    def test_get_user_channel_dict_user_miss(self):
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_1]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_OID_2]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_2]))

        self.assertEqual(
            ProfileManager.get_users_exist_channel_dict([ObjectId()]),
            {}
        )

    def test_get_user_channel_dict_partial_user_miss(self):
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_1]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID,
                                          ProfileOids=[self.PROF_OID_2]))
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                          ProfileOids=[self.PROF_OID_2]))

        self.assertEqual(
            ProfileManager.get_users_exist_channel_dict([self.USER_OID, ObjectId()]),
            {self.USER_OID: {self.CHANNEL_OID_2}}
        )

    def test_get_perms(self):
        mdls = [
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                            ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                            ProfilePermission.PRF_CONTROL_MEMBER.code_str: True}),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        ]

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.NORMAL) \
            .union({ProfilePermission.AR_ACCESS_PINNED_MODULE,
                    ProfilePermission.PRF_CONTROL_SELF,
                    ProfilePermission.PRF_CONTROL_MEMBER})

        self.assertEqual(ProfileManager.get_permissions(mdls), perms)

    def test_get_perms_all_normal(self):
        mdls = [
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC"),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        ]

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.NORMAL)

        self.assertEqual(ProfileManager.get_permissions(mdls), perms)

    def test_get_perms_level(self):
        mdls = [
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC", PermissionLevel=PermissionLevel.MOD),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
        ]

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.MOD)

        self.assertEqual(ProfileManager.get_permissions(mdls), perms)

    def test_get_perms_mixed(self):
        mdls = [
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC", PermissionLevel=PermissionLevel.MOD),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF",
                                Permission={ProfilePermission.PRF_CED.code_str: True,
                                            ProfilePermission.PRF_CONTROL_SELF.code_str: True})
        ]

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.MOD) \
            .union({ProfilePermission.PRF_CED, ProfilePermission.PRF_CONTROL_SELF})

        self.assertEqual(ProfileManager.get_permissions(mdls), perms)

    def test_get_perms_empty(self):
        self.assertEqual(ProfileManager.get_permissions([]), set())

    def test_get_user_perms(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                  Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                              ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                              ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")

        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.NORMAL) \
            .union({ProfilePermission.AR_ACCESS_PINNED_MODULE,
                    ProfilePermission.PRF_CONTROL_SELF,
                    ProfilePermission.PRF_CONTROL_MEMBER})

        self.assertEqual(ProfileManager.get_user_permissions(self.CHANNEL_OID, self.USER_OID), perms)

    def test_get_user_perms_all_normal(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")

        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.NORMAL)

        self.assertEqual(ProfileManager.get_user_permissions(self.CHANNEL_OID, self.USER_OID), perms)

    def test_get_user_perms_level(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC", PermissionLevel=PermissionLevel.MOD)
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")

        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.MOD)

        self.assertEqual(ProfileManager.get_user_permissions(self.CHANNEL_OID, self.USER_OID), perms)

    def test_get_user_perms_mixed(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC", PermissionLevel=PermissionLevel.MOD)
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF",
                                   Permission={ProfilePermission.PRF_CED.code_str: True,
                                               ProfilePermission.PRF_CONTROL_SELF.code_str: True})
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )

        perms = ProfilePermissionDefault.get_overridden_permissions(PermissionLevel.MOD) \
            .union({ProfilePermission.PRF_CED, ProfilePermission.PRF_CONTROL_SELF})

        self.assertEqual(ProfileManager.get_user_permissions(self.CHANNEL_OID, self.USER_OID), perms)

    def test_get_user_perms_miss(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC", PermissionLevel=PermissionLevel.MOD)
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF",
                                   Permission={ProfilePermission.PRF_CED.code_str: True,
                                               ProfilePermission.PRF_CONTROL_SELF.code_str: True})
        ProfileDataManager.insert_one_model(mdl)
        ProfileDataManager.insert_one_model(mdl2)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )

        self.assertEqual(ProfileManager.get_user_permissions(ObjectId(), self.USER_OID), set())
        self.assertEqual(ProfileManager.get_user_permissions(self.CHANNEL_OID, ObjectId()), set())

    def test_get_user_perms_no_data(self):
        self.assertEqual(ProfileManager.get_user_permissions(self.CHANNEL_OID, self.USER_OID), set())

    def test_get_channel_prof_conn(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[self.PROF_OID_1])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_1])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertModelSequenceEqual(
            ProfileManager.get_channel_prof_conn(self.CHANNEL_OID),
            [mdl, mdl2]
        )

    def test_get_channel_prof_conn_multi(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[self.PROF_OID_1])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_1])
        mdl3 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_2])
        mdl4 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_2])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)
        UserProfileManager.insert_one_model(mdl3)
        UserProfileManager.insert_one_model(mdl4)

        self.assertModelSetEqual(
            set(ProfileManager.get_channel_prof_conn([self.CHANNEL_OID, self.CHANNEL_OID_2])),
            {mdl, mdl2, mdl3, mdl4}
        )

    def test_get_channel_prof_conn_available_only(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_1])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertModelSetEqual(
            set(ProfileManager.get_channel_prof_conn(self.CHANNEL_OID, available_only=True)),
            {mdl2}
        )

    def test_get_channel_prof_conn_no_available(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertModelSetEqual(
            set(ProfileManager.get_channel_prof_conn(self.CHANNEL_OID)),
            {mdl, mdl2}
        )
        self.assertModelSetEqual(
            set(ProfileManager.get_channel_prof_conn(self.CHANNEL_OID, available_only=True)),
            set()
        )

    def test_get_channel_prof_conn_no_member(self):
        self.assertModelSetEqual(
            set(ProfileManager.get_channel_prof_conn(self.CHANNEL_OID)),
            set()
        )
        self.assertModelSetEqual(
            set(ProfileManager.get_channel_prof_conn(self.CHANNEL_OID, available_only=True)),
            set()
        )

    def test_get_channel_prof_conn_miss(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertModelSequenceEqual(
            ProfileManager.get_channel_prof_conn(ObjectId()),
            []
        )
        self.assertModelSequenceEqual(
            ProfileManager.get_channel_prof_conn(ObjectId(), available_only=True),
            []
        )

    def test_get_member_oids(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[self.PROF_OID_1])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_1])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertEqual(
            ProfileManager.get_channel_member_oids(self.CHANNEL_OID),
            {self.USER_OID, self.USER_OID_2}
        )

    def test_get_member_oids_multi(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[self.PROF_OID_1])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID_2, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_2])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertEqual(
            ProfileManager.get_channel_member_oids([self.CHANNEL_OID, self.CHANNEL_OID_2]),
            {self.USER_OID, self.USER_OID_2}
        )

    def test_get_member_oids_available_only(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[self.PROF_OID_1])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertEqual(
            ProfileManager.get_channel_member_oids([self.CHANNEL_OID, self.CHANNEL_OID_2], available_only=True),
            {self.USER_OID_2}
        )

    def test_get_member_oids_no_available(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertEqual(
            ProfileManager.get_channel_member_oids(self.CHANNEL_OID),
            {self.USER_OID, self.USER_OID_2}
        )
        self.assertEqual(
            ProfileManager.get_channel_member_oids(self.CHANNEL_OID, available_only=True),
            set()
        )

    def test_get_member_oids_no_member(self):
        self.assertEqual(
            ProfileManager.get_channel_member_oids(self.CHANNEL_OID),
            set()
        )
        self.assertEqual(
            ProfileManager.get_channel_member_oids(self.CHANNEL_OID, available_only=True),
            set()
        )

    def test_get_member_oids_miss(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        self.assertEqual(
            ProfileManager.get_channel_member_oids(ObjectId()),
            set()
        )
        self.assertEqual(
            ProfileManager.get_channel_member_oids(ObjectId(), available_only=True),
            set()
        )

    def test_get_available_conns(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                            ProfileOids=[self.PROF_OID_1])
        mdl2 = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                             ProfileOids=[])
        UserProfileManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(mdl2)

        # For some reason, `assertSetEqual` is not working
        self.assertModelSequenceEqual(list(ProfileManager.get_available_connections()), [mdl], ignore_oid=False)

    def test_get_available_conns_empty(self):
        self.assertModelSetEqual(set(ProfileManager.get_available_connections()), set(), ignore_oid=False)

    # TEST: Starts here

    def test_get_attachable(self):
        pass
