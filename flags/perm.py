from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagPrefixedDoubleEnum


class PermissionCategory(FlagPrefixedDoubleEnum):
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !! Add corresponding HTML file under `templates/account/channel/perm` with code as the name of the file. !!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    0xx - Miscellaneous
        1 - Normal

    1xx - Auto Reply
        101 - Access Pinned Module

    2xx - Members Control
        201 - Change Managers

    3xx - Channel Control
        301 - Adjust features
        302 - Adjust Votes
        303 - Adjust Info Privacy
    """

    @property
    def code_prefix(self) -> str:
        return "_"

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
        301, _("Channel: Features availability"), \
        _("User who has this permission can change the availability of the certain features.")

    CNL_ADJUST_VOTES = \
        302, _("Channel: Vote for managers"), \
        _("User who has this permission can change the availability of voting to promote members.")

    CNL_ADJUST_PRIVACY = \
        303, _("Channel: Info Privacy"), \
        _("User who has this permission can change the privacy of the channel info.")


class PermissionCategoryDefault:
    _Cache = {}

    _Preset = (
        (PermissionCategory.NORMAL, True),
        (PermissionCategory.AR_ACCESS_PINNED_MODULE, False),
        (PermissionCategory.MBR_CHANGE_MEMBERS, False),
        (PermissionCategory.CNL_ADJUST_FEATURES, False),
        (PermissionCategory.CNL_ADJUST_VOTES, False)
    )

    _ModOverride = (
        (PermissionCategory.AR_ACCESS_PINNED_MODULE, True),
    )

    _AdminOverride = (
        (PermissionCategory.MBR_CHANGE_MEMBERS, True),
    )

    @staticmethod
    def get_default_preset() -> dict:
        if "default" not in PermissionCategoryDefault._Cache:
            PermissionCategoryDefault._Cache["default"] = {k: v for k, v in PermissionCategoryDefault._Preset}
        return PermissionCategoryDefault._Cache["default"]

    @staticmethod
    def get_default_preset_dict() -> dict:
        return {k.code_str: v for k, v in PermissionCategoryDefault.get_default_preset().items()}

    @staticmethod
    def get_default(category: PermissionCategory):
        return PermissionCategoryDefault.get_default_preset().get(category, False)

    @staticmethod
    def get_mod_preset():
        if "mod" not in PermissionCategoryDefault._Cache:
            d = PermissionCategoryDefault.get_default_preset()

            for cat, val in PermissionCategoryDefault._ModOverride:
                d[cat] = val

            PermissionCategoryDefault._Cache["mod"] = d

        return PermissionCategoryDefault._Cache["mod"]

    @staticmethod
    def get_mod_override():
        return PermissionCategoryDefault._ModOverride

    @staticmethod
    def get_mod(category: PermissionCategory):
        return PermissionCategoryDefault.get_mod_preset().get(category, False)

    @staticmethod
    def get_admin_preset():
        if "admin" not in PermissionCategoryDefault._Cache:
            d = PermissionCategoryDefault.get_mod_preset()

            for cat, val in PermissionCategoryDefault._AdminOverride:
                d[cat] = val

            PermissionCategoryDefault._Cache["admin"] = d

        return PermissionCategoryDefault._Cache["admin"]

    @staticmethod
    def get_admin_override():
        return PermissionCategoryDefault._AdminOverride

    @staticmethod
    def get_admin(category: PermissionCategory):
        return PermissionCategoryDefault.get_admin_preset().get(category, False)
