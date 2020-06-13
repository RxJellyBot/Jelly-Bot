from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from extutils.color import ColorFactory
from flags import ProfilePermissionDefault, PermissionLevel, ProfilePermission
from models import Model, ChannelProfileModel, ChannelProfileConnectionModel, PermissionPromotionRecordModel

from ._test_base import TestModel

__all__ = ["TestChannelProfileModel", "TestChannelProfileConnectionModel", "TestPermissionPromotionRecordModel"]


class TestChannelProfileModel(TestModel.TestClass):
    CHANNEL_OID = ObjectId()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ChannelProfileModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("c", "ChannelOid"): TestChannelProfileModel.CHANNEL_OID
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("n", "Name"): ("-", "ChannelName"),
            ("col", "Color"): (ColorFactory.DEFAULT, ColorFactory.WHITE),
            ("promo", "PromoVote"): (0, 5),
            ("perm", "Permission"):
                (ProfilePermissionDefault.get_default_code_str_dict(),
                 ProfilePermissionDefault.get_default_code_str_dict({ProfilePermission.AR_ACCESS_PINNED_MODULE,
                                                                     ProfilePermission.CNL_ADJUST_PRIVACY})),
            ("plv", "PermissionLevel"): (PermissionLevel.NORMAL, PermissionLevel.NORMAL),
            ("e-kw", "EmailKeyword"): ([], ["A", "B"])
        }

    def test_is_mod_admin(self):
        # (<MODEL>, is_mod, is_admin), ...
        data = (
            (self.get_constructed_model(plv=PermissionLevel.NORMAL), False, False),
            (self.get_constructed_model(plv=PermissionLevel.MOD), True, False),
            (self.get_constructed_model(plv=PermissionLevel.ADMIN), True, True)
        )

        for model, is_mod, is_admin in data:
            with self.subTest(expected_is_mod=is_mod, model=model):
                self.assertEqual(model.is_mod, is_mod)
            with self.subTest(expected_is_admin=is_admin, model=model):
                self.assertEqual(model.is_admin, is_admin)

    def test_permission_set(self):
        perm_dict = {
            ProfilePermission.AR_ACCESS_PINNED_MODULE: True,
            ProfilePermission.CNL_ADJUST_PRIVACY: True
        }
        mdl = self.get_constructed_model(perm=perm_dict)

        expected = {perm for perm, active in ProfilePermissionDefault.get_default_dict().items() if active}
        expected.update(perm_dict)

        self.assertSetEqual(mdl.permission_set, expected)

    def test_permission_list(self):
        perm_dict = {
            ProfilePermission.AR_ACCESS_PINNED_MODULE: True,
            ProfilePermission.CNL_ADJUST_PRIVACY: True
        }
        mdl = self.get_constructed_model(perm=perm_dict)

        expected = {perm for perm, active in ProfilePermissionDefault.get_default_dict().items() if active}
        expected.update(perm_dict)

        self.assertListEqual(
            mdl.permission_list,
            [ProfilePermission.NORMAL, ProfilePermission.AR_ACCESS_PINNED_MODULE, ProfilePermission.CNL_ADJUST_PRIVACY]
        )


class TestChannelProfileConnectionModel(TestModel.TestClass):
    CHANNEL_OID = ObjectId()
    USER_OID = ObjectId()
    PROFILE_OIDS = [ObjectId(), ObjectId()]

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ChannelProfileConnectionModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("c", "ChannelOid"): TestChannelProfileConnectionModel.CHANNEL_OID,
            ("u", "UserOid"): TestChannelProfileConnectionModel.USER_OID,
            ("p", "ProfileOids"): TestChannelProfileConnectionModel.PROFILE_OIDS
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("s", "Starred"): (False, True),
        }

    def test_available(self):
        mdl = self.get_constructed_model(p=[ObjectId(), ObjectId()])
        self.assertTrue(mdl.available)

        mdl = self.get_constructed_model(p=[])
        self.assertFalse(mdl.available)


class TestPermissionPromotionRecordModel(TestModel.TestClass):
    SUPPORTER_OID = ObjectId()
    TARGET_OID = ObjectId()
    PROFILE_OID = ObjectId()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return PermissionPromotionRecordModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("s", "SupporterOid"): TestPermissionPromotionRecordModel.SUPPORTER_OID,
            ("t", "TargetOid"): TestPermissionPromotionRecordModel.TARGET_OID,
            ("p", "ProfileOid"): TestPermissionPromotionRecordModel.PROFILE_OID,
        }
