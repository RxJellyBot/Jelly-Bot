from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from flags import Platform, ProfilePermission, ProfilePermissionDefault
from models import OID_KEY, ChannelModel, ChannelProfileModel, ChannelConfigModel, ChannelProfileConnectionModel
from models.exceptions import RequiredKeyNotFilledError, InvalidModelFieldError
from mongodb.factory import ChannelManager
from mongodb.factory.prof import ProfileManager, ProfileDataManager, UserProfileManager
from mongodb.factory.results import OperationOutcome, WriteOutcome, GetOutcome, UpdateOutcome, ArgumentParseResult
from strres.mongodb import Profile
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestProfileManagerCRUD"]


class TestProfileManagerCRUD(TestModelMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()
    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()
    PROF_OID_1 = ObjectId()
    PROF_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [ProfileManager]

    def test_create_default(self):
        ChannelManager.clear()

        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileManager.create_default_profile(channel_oid)

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertModelEqual(result.model,
                              ChannelProfileModel(ChannelOid=channel_oid, Name=str(Profile.DEFAULT_PROFILE_NAME)))

        d = ChannelManager.find_one({OID_KEY: channel_oid})
        self.assertEqual(d[ChannelModel.Config.key][ChannelConfigModel.DefaultProfileOid.key], result.model.id)

    def test_create_default_no_channel(self):
        result = ProfileManager.create_default_profile(self.CHANNEL_OID)

        self.assertEqual(result.outcome, WriteOutcome.X_CHANNEL_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

    def test_create_default_not_to_set(self):
        ChannelManager.clear()

        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileManager.create_default_profile(channel_oid, set_to_channel=False)

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertIsNotNone(result.model)

        d = ChannelManager.find_one({OID_KEY: channel_oid})
        self.assertIsNotNone(d)
        self.assertEqual(d[ChannelModel.Config.key].get(ChannelConfigModel.DefaultProfileOid.key), result.model.id)

    def test_create_default_not_to_set_no_channel(self):
        ChannelManager.clear()

        result = ProfileManager.create_default_profile(self.CHANNEL_OID, set_to_channel=False)

        self.assertEqual(result.outcome, WriteOutcome.X_CHANNEL_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

        d = ChannelManager.find_one({OID_KEY: self.CHANNEL_OID})
        self.assertIsNone(d)

    def test_register_new(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id
        ProfileManager.register_new_default(channel_oid, self.USER_OID)

        result = ProfileManager.register_new(self.USER_OID, ChannelOid=channel_oid, Name="A")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({ChannelProfileModel.Name.key: "A"}, parse_cls=ChannelProfileModel),
            result.model)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1)

    def test_register_new_missing_args(self):
        result = ProfileManager.register_new(self.USER_OID, Name="A")

        self.assertEqual(result.outcome, WriteOutcome.X_REQUIRED_NOT_FILLED)
        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, RequiredKeyNotFilledError)
        self.assertEqual(result.attach_outcome, OperationOutcome.X_NOT_EXECUTED)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_register_new_args_type_mismatch(self):
        result = ProfileManager.register_new(self.USER_OID, ChannelOid=self.CHANNEL_OID, Name=object())

        self.assertEqual(result.outcome, WriteOutcome.X_TYPE_MISMATCH)
        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, InvalidModelFieldError)
        self.assertEqual(result.attach_outcome, OperationOutcome.X_NOT_EXECUTED)
        self.assertEqual(ProfileDataManager.count_documents({}), 0)

    def test_register_new_user_not_found(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileManager.register_new(self.USER_OID, ChannelOid=channel_oid, Name="A")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertEqual(ProfileDataManager.count_documents({}), 2)
        self.assertEqual(
            ProfileDataManager.count_documents({ChannelProfileModel.Name.key: str(Profile.DEFAULT_PROFILE_NAME)}), 1
        )
        self.assertEqual(
            ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1
        )
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({ChannelProfileModel.Name.key: "A"}, parse_cls=ChannelProfileModel),
            result.model
        )

    def test_register_new_name_conflict(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        ProfileManager.register_new(self.USER_OID, ChannelOid=channel_oid, Name="A")
        result = ProfileManager.register_new(self.USER_OID, ChannelOid=channel_oid, Name="A")

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({ChannelProfileModel.Name.key: "A"}, parse_cls=ChannelProfileModel),
            result.model)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1)

    def test_register_new_insuf_perm(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        ProfileManager.register_new_default(channel_oid, self.USER_OID)
        result = ProfileManager.register_new(
            self.USER_OID, ChannelOid=channel_oid, Name="A",
            Permission=ProfilePermissionDefault.get_default_code_str_dict({ProfilePermission.MBR_CHANGE_MEMBERS}))

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.X_NOT_EXECUTED)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_register_new_via_parsed_args(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        ProfileManager.register_new_default(channel_oid, self.USER_OID)
        result = ProfileManager.register_new(
            self.USER_OID,
            ProfileManager.process_create_profile_kwargs({
                "ChannelOid": channel_oid,
                "Name": "A"
            })
        )

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertEqual(result.parse_arg_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(ProfileDataManager.find_one_casted(
            {ChannelProfileModel.Name.key: "A"}, parse_cls=ChannelProfileModel),
            result.model)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1)

    def test_register_new_parsed_args_failed(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        ProfileManager.register_new_default(channel_oid, self.USER_OID)
        result = ProfileManager.register_new(
            self.USER_OID,
            ProfileManager.process_create_profile_kwargs({
                "ChannelOid": channel_oid,
                "Name": object()
            })
        )

        self.assertEqual(result.outcome, WriteOutcome.X_NOT_EXECUTED)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.X_NOT_EXECUTED)
        self.assertEqual(result.parse_arg_outcome, OperationOutcome.X_VALUE_TYPE_MISMATCH)
        self.assertEqual(ProfileDataManager.count_documents({}), 1)

    def test_register_new_default(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id
        ProfileManager.register_new_default(channel_oid, self.USER_OID)

        result = ProfileManager.register_new_default(channel_oid, self.USER_OID)

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel), result.model)

    def test_register_new_default_channel_not_found(self):
        ChannelManager.clear()

        result = ProfileManager.register_new_default(self.CHANNEL_OID, self.USER_OID)

        self.assertEqual(result.outcome, GetOutcome.X_CHANNEL_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.X_NOT_EXECUTED)

    def test_register_new_default_user_not_found(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileManager.register_new_default(channel_oid, self.USER_OID)

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel), result.model)

    def test_register_new_model(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id
        ProfileManager.register_new_default(channel_oid, self.USER_OID)

        result = ProfileManager.register_new_model(
            self.USER_OID, ChannelProfileModel(ChannelOid=channel_oid, Name="A"))

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({ChannelProfileModel.Name.key: "A"}, parse_cls=ChannelProfileModel),
            result.model)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1)

    def test_register_new_model_user_not_found(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileManager.register_new_model(
            self.USER_OID, ChannelProfileModel(ChannelOid=channel_oid, Name="A"))

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({ChannelProfileModel.Name.key: "A"}, parse_cls=ChannelProfileModel),
            result.model
        )
        self.assertEqual(ProfileDataManager.count_documents({}), 2)
        self.assertEqual(
            ProfileDataManager.count_documents({ChannelProfileModel.Name.key: str(Profile.DEFAULT_PROFILE_NAME)}),
            1
        )
        self.assertEqual(
            ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}),
            1
        )

    def test_register_new_model_name_conflict(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        ProfileManager.register_new(self.USER_OID, ChannelOid=channel_oid, Name="A")
        result = ProfileManager.register_new_model(
            self.USER_OID, ChannelProfileModel(ChannelOid=channel_oid, Name="A"))

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertEqual(result.attach_outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({ChannelProfileModel.Name.key: "A"}, parse_cls=ChannelProfileModel),
            result.model)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1)

    def test_register_new_model_insuf_perm(self):
        ChannelManager.clear()
        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id
        ProfileManager.register_new_default(channel_oid, self.USER_OID)

        result = ProfileManager.register_new_model(
            self.USER_OID,
            ChannelProfileModel(
                ChannelOid=channel_oid, Name="A",
                Permission=ProfilePermissionDefault.get_default_code_str_dict({ProfilePermission.MBR_CHANGE_MEMBERS})))

        self.assertEqual(result.outcome, WriteOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertEqual(result.attach_outcome, OperationOutcome.X_NOT_EXECUTED)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_update(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)

        result = ProfileManager.update_profile(self.CHANNEL_OID, self.USER_OID, mdl.id,
                                               **{ChannelProfileModel.Name.key: "B"})

        self.assertEqual(result, UpdateOutcome.O_UPDATED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="B")
        )

    def test_update_addl_args(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)

        result = ProfileManager.update_profile(
            self.CHANNEL_OID, self.USER_OID, mdl.id,
            **{ChannelProfileModel.Name.key: "B", "ABCDEF": "B"})

        self.assertEqual(result, UpdateOutcome.O_PARTIAL_ARGS_REMOVED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="B")
        )

    def test_update_invalid_args(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)

        result = ProfileManager.update_profile(
            self.CHANNEL_OID, self.USER_OID, mdl.id,
            **{ChannelProfileModel.Name.key: "B", ChannelProfileModel.Color.key: object()})

        self.assertEqual(result, UpdateOutcome.O_PARTIAL_ARGS_INVALID)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="B")
        )

    def test_update_insuf_perm(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[mdl.id]))

        result = ProfileManager.update_profile(
            self.CHANNEL_OID, self.USER_OID, mdl.id,
            **{ChannelProfileModel.Name.key: "B",
               f"{ChannelProfileModel.Permission.key}.{ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str}": True})

        self.assertEqual(result, UpdateOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        )

    def test_update_uneditable(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[mdl.id]))

        result = ProfileManager.update_profile(
            self.CHANNEL_OID, self.USER_OID, mdl.id,
            **{ChannelProfileModel.ChannelOid.key: self.CHANNEL_OID_2})

        self.assertEqual(result, UpdateOutcome.X_UNEDITABLE)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        )

    def test_update_via_parsed(self):
        arg_result = ArgumentParseResult(OperationOutcome.O_COMPLETED, None, {ChannelProfileModel.Name.key: "B"})

        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)

        result = ProfileManager.update_profile(self.CHANNEL_OID, self.USER_OID, mdl.id, arg_result)

        self.assertEqual(result, UpdateOutcome.O_UPDATED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="B")
        )

    def test_update_via_parsed_failed(self):
        arg_result = ArgumentParseResult(OperationOutcome.X_NOT_EXECUTED, None, {})

        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)

        result = ProfileManager.update_profile(self.CHANNEL_OID, self.USER_OID, mdl.id, arg_result)

        self.assertEqual(result, UpdateOutcome.X_ARGS_PARSE_FAILED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        )

    def test_update_via_parsed_insuf_perm(self):
        arg_result = ArgumentParseResult(
            OperationOutcome.O_COMPLETED, None,
            {ChannelProfileModel.Name.key: "B",
             f"{ChannelProfileModel.Permission.key}.{ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str}": True})

        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[mdl.id]))

        result = ProfileManager.update_profile(self.CHANNEL_OID, self.USER_OID, mdl.id, arg_result)

        self.assertEqual(result, UpdateOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        )

    def test_star(self):
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[]))

        self.assertTrue(ProfileManager.update_channel_star(self.CHANNEL_OID, self.USER_OID, True))
        self.assertEqual(UserProfileManager.count_documents({ChannelProfileConnectionModel.Starred.key: False}), 0)
        self.assertEqual(UserProfileManager.count_documents({ChannelProfileConnectionModel.Starred.key: True}), 1)

        self.assertFalse(ProfileManager.update_channel_star(self.CHANNEL_OID, self.USER_OID, True))
        self.assertEqual(UserProfileManager.count_documents({ChannelProfileConnectionModel.Starred.key: False}), 0)
        self.assertEqual(UserProfileManager.count_documents({ChannelProfileConnectionModel.Starred.key: True}), 1)

        self.assertTrue(ProfileManager.update_channel_star(self.CHANNEL_OID, self.USER_OID, False))
        self.assertEqual(UserProfileManager.count_documents({ChannelProfileConnectionModel.Starred.key: False}), 1)
        self.assertEqual(UserProfileManager.count_documents({ChannelProfileConnectionModel.Starred.key: True}), 0)

    def test_star_not_found(self):
        self.assertFalse(ProfileManager.update_channel_star(self.CHANNEL_OID, self.USER_OID, False))
        self.assertFalse(ProfileManager.update_channel_star(self.CHANNEL_OID, self.USER_OID, True))

    def test_attach_bypass_existence_check(self):
        mdl = ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[])
        UserProfileManager.insert_one_model(mdl)

        self.assertNotEqual(
            ProfileManager.attach_profile(self.CHANNEL_OID, self.USER_OID, mdl.id, bypass_existence_check=True),
            OperationOutcome.X_PROFILE_NOT_FOUND_OID
        )

    def test_delete(self):
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

        result = ProfileManager.delete_profile(self.CHANNEL_OID, mdl2.id, self.USER_OID)

        self.assertEqual(result, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID},
                                               parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id])
        )
        self.assertModelEqual(
            UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2},
                                               parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                          ProfileOids=[mdl.id])
        )
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({OID_KEY: mdl.id}, parse_cls=ChannelProfileModel), mdl
        )
        self.assertIsNone(ProfileDataManager.find_one({OID_KEY: mdl2.id}))

    def test_delete_insuf_perm(self):
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

        result = ProfileManager.delete_profile(self.CHANNEL_OID, mdl2.id, self.USER_OID_2)

        self.assertEqual(result, OperationOutcome.X_INSUFFICIENT_PERMISSION)
        self.assertModelEqual(
            UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID},
                                               parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )
        self.assertModelEqual(
            UserProfileManager.find_one_casted({ChannelProfileConnectionModel.UserOid.key: self.USER_OID_2},
                                               parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID_2,
                                          ProfileOids=[mdl2.id])
        )
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({OID_KEY: mdl.id}, parse_cls=ChannelProfileModel), mdl
        )
        self.assertModelEqual(
            ProfileDataManager.find_one_casted({OID_KEY: mdl2.id}, parse_cls=ChannelProfileModel), mdl2
        )

    def test_delete_not_exists(self):
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[ObjectId()]))

        result = ProfileManager.delete_profile(self.CHANNEL_OID, ObjectId(), self.USER_OID)

        self.assertEqual(result, OperationOutcome.X_PROFILE_NOT_FOUND_OID)

    def test_mark_unavailable_async(self):
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

        ProfileManager.mark_unavailable_async(self.CHANNEL_OID, self.USER_OID).join()

        self.assertModelEqual(
            UserProfileManager.find_one_casted(parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[])
        )

    def test_mark_unavailable_async_miss(self):
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

        ProfileManager.mark_unavailable_async(self.CHANNEL_OID, self.USER_OID_2).join()

        self.assertModelEqual(
            UserProfileManager.find_one_casted(parse_cls=ChannelProfileConnectionModel),
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID,
                                          ProfileOids=[mdl.id, mdl2.id])
        )
