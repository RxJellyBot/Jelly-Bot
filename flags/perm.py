from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum


class PermissionCategory(FlagDoubleEnum):
    """
    0xx - Miscellaneous
        1 - Normal

    1xx - Auto Reply
        101 - Access Pinned Module

    2xx - Members Control
        201 - Change Managers

    3xx - Channel Control
        301 - Adjust features
        302 - Adjust Votes
    """
    @classmethod
    def default(cls):
        raise PermissionCategory.NORMAL

    NORMAL = \
        1, _("Normal"), \
        _("User who has this permission can do all normal operations.")

    AR_ACCESS_PINNED_MODULE = \
        101, _("Auto-Reply: Access Pinned Module"), \
        _("User who has this permission can access the Pinned property of the Auto-Reply modules.")

    MBR_CHANGE_MEMBERS = \
        201, _("Members: Change Managers"), \
        _("User who has this permission can change the members of managers.")

    CNL_ADJUST_FEATURES = \
        301, _("Channel: Adjust features availability"), \
        _("User who has this permission can access the availability of the certain features.")

    CNL_ADJUST_VOTES = \
        302, _("Channel: Vote for managers"), \
        _("User who has this permission can access the availability of voting to promote members.")


class PermissionCategoryDefault:
    _Cache = {}

    _Preset = (
        (PermissionCategory.NORMAL, True),
        (PermissionCategory.AR_ACCESS_PINNED_MODULE, False),
        (PermissionCategory.MBR_CHANGE_MEMBERS, False)
    )

    @staticmethod
    def get_default_preset():
        if "default" not in PermissionCategoryDefault._Cache:
            PermissionCategoryDefault._Cache["default"] = {k: v for k, v in PermissionCategoryDefault._Preset}
        return PermissionCategoryDefault._Cache["default"]

    @staticmethod
    def get_default(category: PermissionCategory):
        return PermissionCategoryDefault.get_default_preset().get(category, False)

    @staticmethod
    def get_mod_preset():
        if "mod" not in PermissionCategoryDefault._Cache:
            d = PermissionCategoryDefault.get_default_preset()
            d[PermissionCategory.AR_ACCESS_PINNED_MODULE] = True

            PermissionCategoryDefault._Cache["mod"] = d

        return PermissionCategoryDefault._Cache["mod"]

    @staticmethod
    def get_mod(category: PermissionCategory):
        return PermissionCategoryDefault.get_mod_preset().get(category, False)

    @staticmethod
    def get_admin_preset():
        if "admin" not in PermissionCategoryDefault._Cache:
            d = PermissionCategoryDefault.get_mod_preset()
            d[PermissionCategory.MBR_CHANGE_MEMBERS] = True

            PermissionCategoryDefault._Cache["admin"] = d

        return PermissionCategoryDefault._Cache["admin"]

    @staticmethod
    def get_admin(category: PermissionCategory):
        return PermissionCategoryDefault.get_admin_preset().get(category, False)
