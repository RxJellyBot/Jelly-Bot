from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from flags import Platform, ProfilePermissionDefault, ProfilePermission, PermissionLevel
from models import OID_KEY, ChannelProfileModel, ChannelModel, ChannelConfigModel
from mongodb.factory import ChannelManager
from mongodb.factory.prof_base import ProfileDataManager
from mongodb.factory.results import WriteOutcome, GetOutcome, UpdateOutcome
from strres.mongodb import Profile
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestProfileDataManager"]


class TestProfileDataManager(TestModelMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [ProfileDataManager]

    def _insert_sample_profiles(self):
        mdls = [
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="AA"),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="BB"),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="AC"),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="AA"),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="AB"),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID_2, Name="AD")
        ]
        ProfileDataManager.insert_many(mdls)

        return mdls

    def _insert_profiles(self):
        mdls = [
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="A",
                Permission=ProfilePermissionDefault.get_default_code_str_dict({ProfilePermission.PRF_CED})),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="B", PermissionLevel=PermissionLevel.MOD),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="C"),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="D", PermissionLevel=PermissionLevel.ADMIN),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="E",
                Permission=ProfilePermissionDefault.get_default_code_str_dict(
                    {ProfilePermission.AR_ACCESS_PINNED_MODULE})),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID_2, Name="F",
                Permission=ProfilePermissionDefault.get_default_code_str_dict(
                    {ProfilePermission.AR_ACCESS_PINNED_MODULE}))
        ]

        ProfileDataManager.insert_many(mdls)

        return mdls

    def test_add_duplicate(self):
        self.assertEqual(
            ProfileDataManager.insert_one_model(ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A"))[0],
            WriteOutcome.O_INSERTED)
        self.assertEqual(
            ProfileDataManager.insert_one_model(ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A"))[0],
            WriteOutcome.O_DATA_EXISTS
        )

    def test_get_profile(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID)
        ProfileDataManager.insert_one(mdl)

        self.assertEqual(ProfileDataManager.get_profile(mdl.id), mdl)

    def test_get_profile_not_found(self):
        self.assertIsNone(ProfileDataManager.get_profile(ObjectId()))

    def test_get_profile_dict(self):
        mdls = self._insert_sample_profiles()

        self.assertEqual(
            ProfileDataManager.get_profile_dict([mdls[0].id, mdls[1].id, mdls[2].id]),
            {
                mdls[0].id: mdls[0],
                mdls[1].id: mdls[1],
                mdls[2].id: mdls[2]
            }
        )

    def test_get_profile_dict_partial(self):
        mdls = self._insert_sample_profiles()

        self.assertEqual(
            ProfileDataManager.get_profile_dict([mdls[0].id, mdls[2].id]),
            {
                mdls[0].id: mdls[0],
                mdls[2].id: mdls[2]
            }
        )

    def test_get_profile_dict_partial_miss(self):
        mdls = self._insert_sample_profiles()

        self.assertEqual(
            ProfileDataManager.get_profile_dict([mdls[0].id, ObjectId()]),
            {mdls[0].id: mdls[0]}
        )

    def test_get_profile_dict_no_channel(self):
        self.assertEqual(ProfileDataManager.get_profile_dict([ObjectId(), ObjectId()]), {})

    def test_get_profile_dict_empty_param(self):
        self._insert_sample_profiles()

        self.assertEqual(ProfileDataManager.get_profile_dict([]), {})

    def test_get_profile_name(self):
        mdls = self._insert_sample_profiles()

        self.assertEqual(ProfileDataManager.get_profile_name(self.CHANNEL_OID, "AA"), mdls[0])
        self.assertEqual(ProfileDataManager.get_profile_name(self.CHANNEL_OID_2, "AD"), mdls[5])
        self.assertIsNone(ProfileDataManager.get_profile_name(self.CHANNEL_OID, "A"))
        self.assertIsNone(ProfileDataManager.get_profile_name(self.CHANNEL_OID, "AD"))

    def test_get_profile_name_strip(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="AA ")
        ProfileDataManager.insert_one_model(mdl)

        self.assertEqual(ProfileDataManager.get_profile_name(self.CHANNEL_OID, " AA "), mdl)
        self.assertEqual(ProfileDataManager.get_profile_name(self.CHANNEL_OID, "AA "), mdl)

    def test_get_profile_name_no_data(self):
        self.assertIsNone(ProfileDataManager.get_profile_name(self.CHANNEL_OID, "AA"))
        self.assertIsNone(ProfileDataManager.get_profile_name(self.CHANNEL_OID_2, "AD"))

    def test_get_channel_profile(self):
        mdls = self._insert_sample_profiles()

        self.assertEqual(list(ProfileDataManager.get_channel_profiles(self.CHANNEL_OID)), [mdls[0], mdls[1], mdls[2]])

    def test_get_channel_profile_with_keyword(self):
        mdls = self._insert_sample_profiles()

        self.assertEqual(list(ProfileDataManager.get_channel_profiles(self.CHANNEL_OID, "A")), [mdls[0], mdls[2]])

    def test_get_channel_profile_channel_miss(self):
        self._insert_sample_profiles()

        self.assertEqual(list(ProfileDataManager.get_channel_profiles(ObjectId())), [])
        self.assertEqual(list(ProfileDataManager.get_channel_profiles(ObjectId(), "A")), [])

    def test_get_channel_profile_no_data(self):
        self.assertEqual(list(ProfileDataManager.get_channel_profiles(self.CHANNEL_OID)), [])

    def test_get_default_profile(self):
        ChannelManager.clear()

        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileDataManager.get_default_profile(channel_oid)

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model,
                              ChannelProfileModel(ChannelOid=channel_oid, Name=str(Profile.DEFAULT_PROFILE_NAME)))

    def test_get_default_profile_channel_miss(self):
        result = ProfileDataManager.get_default_profile(ObjectId())

        self.assertEqual(result.outcome, GetOutcome.X_CHANNEL_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

    def test_get_attachable_no_existing_normal(self):
        mdls = self._insert_profiles()

        self.assertModelSetEqual(
            set(ProfileDataManager.get_attachable_profiles(self.CHANNEL_OID)),
            {mdls[2]}
        )

    def test_get_attachable_no_existing_mod(self):
        mdls = self._insert_profiles()

        self.assertModelSetEqual(
            set(ProfileDataManager.get_attachable_profiles(self.CHANNEL_OID, highest_perm_lv=PermissionLevel.MOD)),
            {mdls[1], mdls[2], mdls[4]}
        )

    def test_get_attachable_has_ced_normal(self):
        mdls = self._insert_profiles()

        self.assertModelSetEqual(
            set(ProfileDataManager.get_attachable_profiles(self.CHANNEL_OID,
                                                           existing_permissions={ProfilePermission.PRF_CED})),
            {mdls[0], mdls[2]}
        )

    def test_get_attachable_has_pin_normal(self):
        mdls = self._insert_profiles()

        self.assertModelSetEqual(
            set(ProfileDataManager.get_attachable_profiles(
                self.CHANNEL_OID, existing_permissions={ProfilePermission.AR_ACCESS_PINNED_MODULE})),
            {mdls[2], mdls[4]}
        )

    def test_get_attachable_no_prof(self):
        self.assertEqual(
            set(ProfileDataManager.get_attachable_profiles(
                self.CHANNEL_OID, existing_permissions={ProfilePermission.AR_ACCESS_PINNED_MODULE})),
            set()
        )

    def test_get_attachable_channel_miss(self):
        self._insert_profiles()

        self.assertEqual(
            set(ProfileDataManager.get_attachable_profiles(
                ObjectId(), existing_permissions={ProfilePermission.AR_ACCESS_PINNED_MODULE})),
            set()
        )

    def test_create_default(self):
        ChannelManager.clear()

        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileDataManager.create_default_profile(channel_oid)

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertModelEqual(result.model,
                              ChannelProfileModel(ChannelOid=channel_oid, Name=str(Profile.DEFAULT_PROFILE_NAME)))

        d = ChannelManager.find_one({OID_KEY: channel_oid})
        self.assertEqual(d[ChannelModel.Config.key][ChannelConfigModel.DefaultProfileOid.key], result.model.id)

    def test_create_default_no_channel(self):
        result = ProfileDataManager.create_default_profile(self.CHANNEL_OID)

        self.assertEqual(result.outcome, WriteOutcome.X_CHANNEL_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

    def test_create_default_not_to_set(self):
        ChannelManager.clear()

        channel_oid = ChannelManager.ensure_register(Platform.LINE, "U123456").model.id

        result = ProfileDataManager.create_default_profile(channel_oid, set_to_channel=False)

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertIsNotNone(result.model)

        d = ChannelManager.find_one({OID_KEY: channel_oid})
        self.assertIsNotNone(d)
        self.assertEqual(d[ChannelModel.Config.key].get(ChannelConfigModel.DefaultProfileOid.key), result.model.id)

    def test_create_default_to_set_no_check_no_channel(self):
        ChannelManager.clear()

        result = ProfileDataManager.create_default_profile(self.CHANNEL_OID, check_channel=False)

        self.assertEqual(result.outcome, WriteOutcome.X_ON_SET_CONFIG)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

        d = ChannelManager.find_one({OID_KEY: self.CHANNEL_OID})
        self.assertIsNone(d)

    def test_create_default_not_to_set_no_channel(self):
        ChannelManager.clear()

        result = ProfileDataManager.create_default_profile(self.CHANNEL_OID, set_to_channel=False)

        self.assertEqual(result.outcome, WriteOutcome.X_CHANNEL_NOT_FOUND)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertIsNone(result.model)

        d = ChannelManager.find_one({OID_KEY: self.CHANNEL_OID})
        self.assertIsNone(d)

    def test_create(self):
        result = ProfileDataManager.create_profile(ChannelOid=self.CHANNEL_OID, Name="A")

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A"))

    def test_create_duplicated(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        result = ProfileDataManager.create_profile(ChannelOid=self.CHANNEL_OID, Name="A")

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertEqual(result.model, mdl)

    def test_create_mdl(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        result = ProfileDataManager.create_profile_model(mdl)

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, mdl)

    def test_create_mdl_duplicated(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        mdl2 = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        result = ProfileDataManager.create_profile_model(mdl2)

        self.assertEqual(result.outcome, WriteOutcome.O_DATA_EXISTS)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.exception)
        self.assertIsInstance(result.exception, DuplicateKeyError)
        self.assertEqual(result.model, mdl)

    def test_update(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        mdl.name = "E"

        update_result = ProfileDataManager.update_profile(mdl.id, **{ChannelProfileModel.Name.key: "E"})
        self.assertEqual(update_result, UpdateOutcome.O_UPDATED)

        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "E"}), 1)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_update_addl_args(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        mdl.name = "E"

        update_result = ProfileDataManager.update_profile(mdl.id, **{ChannelProfileModel.Name.key: "E", "ABCDEF": "G"})
        self.assertEqual(update_result, UpdateOutcome.O_PARTIAL_ARGS_REMOVED)

        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "E"}), 1)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_update_invalid_values(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        mdl.name = "E"

        update_result = ProfileDataManager.update_profile(mdl.id, **{ChannelProfileModel.Name.key: "E",
                                                                     ChannelProfileModel.Color.key: "Black"})
        self.assertEqual(update_result, UpdateOutcome.O_PARTIAL_ARGS_INVALID)

        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "E"}), 1)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_update_addl_args_invalid_values(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        mdl.name = "E"

        update_result = ProfileDataManager.update_profile(mdl.id, **{ChannelProfileModel.Name.key: "E",
                                                                     ChannelProfileModel.Color.key: "Black",
                                                                     "ABCDEF": "G"})
        self.assertEqual(update_result, UpdateOutcome.O_PARTIAL_ARGS_REMOVED)

        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "E"}), 1)
        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_update_no_update_after_validate(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        mdl.name = "E"

        update_result = ProfileDataManager.update_profile(mdl.id, **{ChannelProfileModel.Color.key: "Black",
                                                                     "ABCDEF": "G"})
        self.assertEqual(update_result, UpdateOutcome.X_NOT_EXECUTED)

        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1)

    def test_update_no_update(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)
        mdl.name = "E"

        update_result = ProfileDataManager.update_profile(mdl.id)
        self.assertEqual(update_result, UpdateOutcome.X_NOT_EXECUTED)

        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 1)

    def test_update_no_profile(self):
        update_result = ProfileDataManager.update_profile(ObjectId(), **{ChannelProfileModel.Name.key: "A"})
        self.assertEqual(update_result, UpdateOutcome.X_NOT_FOUND)

        self.assertEqual(ProfileDataManager.count_documents({ChannelProfileModel.Name.key: "A"}), 0)

    def test_delete(self):
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A")
        ProfileDataManager.insert_one_model(mdl)

        self.assertTrue(ProfileDataManager.delete_profile(mdl.id))

        self.assertEqual(ProfileDataManager.count_documents({}), 0)

    def test_delete_no_profile(self):
        self.assertFalse(ProfileDataManager.delete_profile(ObjectId()))

    def test_name_available(self):
        ProfileDataManager.insert_one_model(ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="A"))

        self.assertFalse(ProfileDataManager.is_name_available(self.CHANNEL_OID, "A"))
        self.assertFalse(ProfileDataManager.is_name_available(self.CHANNEL_OID, ""))
        self.assertTrue(ProfileDataManager.is_name_available(self.CHANNEL_OID, "AA"))
        self.assertTrue(ProfileDataManager.is_name_available(self.CHANNEL_OID_2, "A"))
