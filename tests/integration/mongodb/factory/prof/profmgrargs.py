from bson import ObjectId

from extutils.color import Color
from flags import ProfilePermission, PermissionLevel, ProfilePermissionDefault
from models import ChannelProfileModel, ChannelProfileConnectionModel
from mongodb.factory import ProfileManager
from mongodb.factory.prof_base import ProfileDataManager, UserProfileManager
from mongodb.factory.results import OperationOutcome, UpdateOutcome
from tests.base import TestDatabaseMixin, TestModelMixin

__all__ = ["TestProfileManagerProcessArgs"]


class TestProfileManagerProcessArgs(TestModelMixin, TestDatabaseMixin):
    CHANNEL_OID = ObjectId()
    CHANNEL_OID_2 = ObjectId()
    USER_OID = ObjectId()
    USER_OID_2 = ObjectId()
    PROF_OID_1 = ObjectId()
    PROF_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [ProfileManager]

    def test_process_create_kwargs(self):
        args_parse_result = ProfileManager.process_create_profile_kwargs({
            "ChannelOid": str(self.CHANNEL_OID),
            "Name": "A",
            "PermissionLevel": PermissionLevel.NORMAL.code_str,
            "Color": "#000000"
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ChannelProfileModel(**args_parse_result.parsed_args),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="A", PermissionLevel=PermissionLevel.NORMAL,
                Color=Color(0)
            )
        )

    def test_process_create_kwargs_addl_args(self):
        args_parse_result = ProfileManager.process_create_profile_kwargs({
            "ChannelOid": str(self.CHANNEL_OID),
            "Name": "A",
            "PermissionLevel": PermissionLevel.NORMAL.code_str,
            "Color": "#000000",
            "A": "B"
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_ADDL_ARGS_OMITTED)
        self.assertModelEqual(
            ChannelProfileModel(**args_parse_result.parsed_args),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="A", PermissionLevel=PermissionLevel.NORMAL,
                Color=Color(0)
            )
        )

    def test_process_create_kwargs_invalid(self):
        args_parse_result = ProfileManager.process_create_profile_kwargs({
            "ChannelOid": "5",
            "Name": "A",
            "PermissionLevel": PermissionLevel.NORMAL.code_str,
            "Color": "#000000"
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.X_INVALID_CHANNEL_OID)
        self.assertIsNone(args_parse_result.parsed_args)

    def test_process_create_kwargs_missing(self):
        args_parse_result = ProfileManager.process_create_profile_kwargs({
            "Name": "A",
            "PermissionLevel": PermissionLevel.NORMAL.code_str,
            "Color": "#000000"
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.X_MISSING_CHANNEL_OID)
        self.assertIsNone(args_parse_result.parsed_args)

    def test_process_create_kwargs_mod(self):
        args_parse_result = ProfileManager.process_create_profile_kwargs({
            "ChannelOid": str(self.CHANNEL_OID),
            "Name": "A",
            "PermissionLevel": PermissionLevel.MOD.code_str,
            "Color": "#000000"
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ChannelProfileModel(**args_parse_result.parsed_args),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="A", PermissionLevel=PermissionLevel.MOD, Color=Color(0)
            )
        )

    def test_process_create_kwargs_given_perm(self):
        args_parse_result = ProfileManager.process_create_profile_kwargs({
            "ChannelOid": str(self.CHANNEL_OID),
            "Name": "A",
            "PermissionLevel": PermissionLevel.NORMAL.code_str,
            f"Permission.{ProfilePermission.MBR_CHANGE_MEMBERS}": "true",
            "Color": "#000000"
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_COMPLETED)
        self.assertModelEqual(
            ChannelProfileModel(**args_parse_result.parsed_args),
            ChannelProfileModel(
                ChannelOid=self.CHANNEL_OID, Name="A", PermissionLevel=PermissionLevel.NORMAL, Color=Color(0),
                Permission=ProfilePermissionDefault.get_default_code_str_dict({ProfilePermission.MBR_CHANGE_MEMBERS}),
            )
        )

    def test_process_edit_kwargs(self):
        args_parse_result = ProfileManager.process_edit_profile_kwargs({
            "Name": "B",
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_COMPLETED)
        self.assertEqual(args_parse_result.parsed_args, {ChannelProfileModel.Name.key: "B"})

        # Test usability of the parsed args
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)

        self.assertEqual(
            ProfileManager.update_profile(self.CHANNEL_OID, self.USER_OID, mdl.id, args_parse_result),
            UpdateOutcome.O_UPDATED
        )
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="B")
        )

    def test_process_edit_kwargs_invalid(self):
        args_parse_result = ProfileManager.process_edit_profile_kwargs({
            "Name": object(),
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.X_VALUE_TYPE_MISMATCH)
        self.assertIsNone(args_parse_result.parsed_args)

    def test_process_edit_kwargs_uneditable(self):
        args_parse_result = ProfileManager.process_edit_profile_kwargs({
            "ChannelOid": self.CHANNEL_OID,
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_READONLY_ARGS_OMITTED)
        self.assertEqual(args_parse_result.parsed_args, {})

    def test_process_edit_kwargs_addl_args(self):
        args_parse_result = ProfileManager.process_edit_profile_kwargs({
            "Name": "B",
            "A": "B"
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_ADDL_ARGS_OMITTED)
        self.assertEqual(args_parse_result.parsed_args, {ChannelProfileModel.Name.key: "B"})

        # Test usability of the parsed args
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC")
        ProfileDataManager.insert_one_model(mdl)

        self.assertEqual(
            ProfileManager.update_profile(self.CHANNEL_OID, self.USER_OID, mdl.id, args_parse_result),
            UpdateOutcome.O_UPDATED)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="B")
        )

    def test_process_edit_kwargs_has_permission(self):
        args_parse_result = ProfileManager.process_edit_profile_kwargs({
            "Permission.101": "true",
            "Permission.301": "true",
        })

        self.assertEqual(args_parse_result.outcome, OperationOutcome.O_COMPLETED)
        self.assertEqual(args_parse_result.parsed_args, {
            f"{ChannelProfileModel.Permission.key}.{ProfilePermission.AR_ACCESS_PINNED_MODULE.code_str}": True,
            f"{ChannelProfileModel.Permission.key}.{ProfilePermission.CNL_ADJUST_FEATURES.code_str}": True
        })

        # Test usability of the parsed args
        mdl = ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC", PermissionLevel=PermissionLevel.ADMIN)
        ProfileDataManager.insert_one_model(mdl)
        UserProfileManager.insert_one_model(
            ChannelProfileConnectionModel(ChannelOid=self.CHANNEL_OID, UserOid=self.USER_OID, ProfileOids=[mdl.id]))

        self.assertTrue(
            ProfileManager.update_profile(self.CHANNEL_OID, self.USER_OID, mdl.id, args_parse_result).is_success)
        self.assertModelEqual(
            ProfileDataManager.find_one_casted(parse_cls=ChannelProfileModel),
            ChannelProfileModel(ChannelOid=self.CHANNEL_OID, Name="ABC", PermissionLevel=PermissionLevel.ADMIN)
        )
