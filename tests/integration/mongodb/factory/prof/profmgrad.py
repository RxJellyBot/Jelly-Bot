from abc import abstractmethod, ABC

from bson import ObjectId

from flags import ProfilePermission
from models import ChannelProfileModel, ChannelProfileConnectionModel
from mongodb.factory import ProfileManager
from mongodb.factory.prof_base import ProfileDataManager, UserProfileManager
from mongodb.factory.results import OperationOutcome
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestProfileManagerAttachName", "TestProfileManagerAttachOid",
           "TestProfileManagerDetachName", "TestProfileManagerDetachOid"]


class TestProfileManagerAttach(ABC):
    class TestClass(TestModelMixin, TestDatabaseMixin):
        CHANNEL_OID = ObjectId()
        CHANNEL_OID_2 = ObjectId()
        USER_OID = ObjectId()
        USER_OID_2 = ObjectId()

        @staticmethod
        def obj_to_clear():
            return [ProfileManager]

        @abstractmethod
        def perm_ctrl_self(self, user_oid: ObjectId, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str) \
                -> OperationOutcome:
            raise NotImplementedError()

        @abstractmethod
        def perm_ctrl_other(self, user_oid: ObjectId, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str,
                            target_oid: ObjectId) \
                -> OperationOutcome:
            raise NotImplementedError()

        @abstractmethod
        def not_found_result(self) -> OperationOutcome:
            raise NotImplementedError()

        def test_suf_perm_ctrl_self(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id]))

            result = self.perm_ctrl_self(self.USER_OID, self.CHANNEL_OID, mdl2.id, "DEF")

            self.assertEqual(result, OperationOutcome.O_COMPLETED)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id, mdl2.id])
            )

        def test_suf_perm_ctrl_other(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id, mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_other(self.USER_OID, self.CHANNEL_OID, mdl.id, "ABC", self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.O_COMPLETED)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id, mdl2.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id, mdl.id])
            )

        def test_insuf_perm_ctrl_self(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_self(self.USER_OID, self.CHANNEL_OID, mdl.id, "ABC")

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )

        def test_insuf_perm_ctrl_other(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_other(self.USER_OID, self.CHANNEL_OID, mdl.id, "ABC", self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id])
            )

        def test_not_found(self):
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[ObjectId()]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[ObjectId()]))

            result = self.perm_ctrl_self(self.USER_OID, self.CHANNEL_OID, ObjectId(), "ABC")
            self.assertEqual(result, self.not_found_result())

            result = self.perm_ctrl_other(self.USER_OID, self.CHANNEL_OID, ObjectId(), "ABC", self.USER_OID_2)
            self.assertEqual(result, self.not_found_result())

        def test_user_not_in_channel(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            ProfileDataManager.insert_one_model(mdl)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl.id]))

            result = self.perm_ctrl_other(self.USER_OID, self.CHANNEL_OID, mdl.id, "ABC", self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_EXECUTOR_NOT_IN_CHANNEL)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl.id])
            )

        def test_target_not_in_channel(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            ProfileDataManager.insert_one_model(mdl)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[]))

            result = self.perm_ctrl_other(self.USER_OID, self.CHANNEL_OID, mdl.id, "ABC", self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_TARGET_NOT_IN_CHANNEL)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[])
            )

        def test_insuf_perm_self(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_self(self.USER_OID, self.CHANNEL_OID, mdl.id, "ABC")

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )

        def test_insuf_perm_self_other(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_other(self.USER_OID, self.CHANNEL_OID, mdl.id, "ABC", self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id])
            )


class TestProfileManagerAttachName(TestProfileManagerAttach.TestClass):
    def not_found_result(self) -> OperationOutcome:
        return OperationOutcome.X_PROFILE_NOT_FOUND_NAME

    def perm_ctrl_self(self, user_oid: ObjectId, channel_oid: ObjectId, prof_oid: ObjectId,
                       prof_name: str) -> OperationOutcome:
        return ProfileManager.attach_profile_name(channel_oid, user_oid, prof_name)

    def perm_ctrl_other(self, user_oid: ObjectId, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str,
                        target_oid: ObjectId) -> OperationOutcome:
        return ProfileManager.attach_profile_name(channel_oid, user_oid, prof_name, target_oid)


class TestProfileManagerAttachOid(TestProfileManagerAttach.TestClass):
    def not_found_result(self) -> OperationOutcome:
        return OperationOutcome.X_PROFILE_NOT_FOUND_OID

    def perm_ctrl_self(self, user_oid: ObjectId, channel_oid: ObjectId, prof_oid: ObjectId,
                       prof_name: str) -> OperationOutcome:
        return ProfileManager.attach_profile(channel_oid, user_oid, prof_oid)

    def perm_ctrl_other(self, user_oid: ObjectId, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str,
                        target_oid: ObjectId) -> OperationOutcome:
        return ProfileManager.attach_profile(channel_oid, user_oid, prof_oid, target_oid)


class TestProfileManagerDetach(ABC):
    class TestClass(TestModelMixin, TestDatabaseMixin):
        CHANNEL_OID = ObjectId()
        CHANNEL_OID_2 = ObjectId()
        USER_OID = ObjectId()
        USER_OID_2 = ObjectId()

        @staticmethod
        def obj_to_clear():
            return [ProfileManager]

        @abstractmethod
        def perm_ctrl_self(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str, user_oid: ObjectId) \
                -> OperationOutcome:
            raise NotImplementedError()

        @abstractmethod
        def perm_ctrl_other(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str, user_oid: ObjectId,
                            target_oid: ObjectId) \
                -> OperationOutcome:
            raise NotImplementedError()

        @abstractmethod
        def perm_ctrl_all(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str, user_oid: ObjectId) \
                -> OperationOutcome:
            raise NotImplementedError()

        @abstractmethod
        def not_found_result(self) -> OperationOutcome:
            raise NotImplementedError()

        def test_suf_perm_ctrl_self(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id, mdl2.id]))

            result = self.perm_ctrl_self(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID)

            self.assertEqual(result, OperationOutcome.O_COMPLETED)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id])
            )

        def test_detach_name_suf_perm_ctrl_other(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id, mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl.id, mdl2.id]))

            result = self.perm_ctrl_other(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID, self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.O_COMPLETED)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id, mdl2.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl.id])
            )

        def test_detach_name_insuf_perm_ctrl_self(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_self(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID)

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )

        def test_detach_name_insuf_perm_ctrl_other(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_other(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID, self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id])
            )

        def test_not_found(self):
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[ObjectId()]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[ObjectId()])), self.USER_OID

            result = self.perm_ctrl_self(self.CHANNEL_OID, ObjectId(), "ABC", self.USER_OID)
            self.assertEqual(result, self.not_found_result())

            result = self.perm_ctrl_other(self.CHANNEL_OID, ObjectId(), "ABC", self.USER_OID, self.USER_OID_2)
            self.assertEqual(result, self.not_found_result())

        def test_detach_name_user_not_in_channel(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            ProfileDataManager.insert_one_model(mdl)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl.id]))

            result = self.perm_ctrl_other(self.CHANNEL_OID, mdl.id, "ABC", self.USER_OID, self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_EXECUTOR_NOT_IN_CHANNEL)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl.id])
            )

        def test_detach_name_target_not_in_channel(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            ProfileDataManager.insert_one_model(mdl)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2, ProfileOids=[]))

            result = self.perm_ctrl_other(self.CHANNEL_OID, mdl.id, "ABC", self.USER_OID, self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_TARGET_NOT_IN_CHANNEL)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[])
            )

        def test_detach_name_insuf_perm_self(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_self(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID)

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )

        def test_detach_name_insuf_perm_self_other(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_other(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID, self.USER_OID_2)

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id])
            )

        def test_detach_all(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id, mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_all(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID)

            self.assertEqual(result, OperationOutcome.O_COMPLETED)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[])
            )

        def test_detach_all_insuf_perm(self):
            mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC",
                                      Permission={ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_SELF.code_str: True,
                                                  ProfilePermission.PRF_CONTROL_MEMBER.code_str: True})
            mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="DEF")
            ProfileDataManager.insert_one_model(mdl)
            ProfileDataManager.insert_one_model(mdl2)
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id]))
            UserProfileManager.insert_one_model(
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id]))

            result = self.perm_ctrl_all(self.CHANNEL_OID, mdl2.id, "DEF", self.USER_OID)

            self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                              ProfileOids=[mdl2.id])
            )
            self.assertModelEqual(
                UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2}),
                ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                              ProfileOids=[mdl2.id])
            )


class TestProfileManagerDetachName(TestProfileManagerDetach.TestClass):
    def not_found_result(self) -> OperationOutcome:
        return OperationOutcome.X_PROFILE_NOT_FOUND_NAME

    def perm_ctrl_self(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str,
                       user_oid: ObjectId) -> OperationOutcome:
        return ProfileManager.detach_profile_name(channel_oid, prof_name, user_oid)

    def perm_ctrl_other(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str, user_oid: ObjectId,
                        target_oid: ObjectId) -> OperationOutcome:
        return ProfileManager.detach_profile_name(channel_oid, prof_name, user_oid, target_oid)

    def perm_ctrl_all(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str, user_oid: ObjectId) \
            -> OperationOutcome:
        return ProfileManager.detach_profile_name(channel_oid, prof_name, user_oid)


class TestProfileManagerDetachOid(TestProfileManagerDetach.TestClass):
    def not_found_result(self) -> OperationOutcome:
        return OperationOutcome.X_PROFILE_NOT_FOUND_OID

    def perm_ctrl_self(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str,
                       user_oid: ObjectId) -> OperationOutcome:
        return ProfileManager.detach_profile(channel_oid, prof_oid, user_oid, user_oid)

    def perm_ctrl_other(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str, user_oid: ObjectId,
                        target_oid: ObjectId) -> OperationOutcome:
        return ProfileManager.detach_profile(channel_oid, prof_oid, user_oid, target_oid)

    def perm_ctrl_all(self, channel_oid: ObjectId, prof_oid: ObjectId, prof_name: str, user_oid: ObjectId) \
            -> OperationOutcome:
        return ProfileManager.detach_profile(channel_oid, prof_oid, user_oid)
