from typing import Dict, Generator, Set

from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum, FlagSingleEnum


class ProfilePermission(FlagDoubleEnum):
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !! Add corresponding HTML file under `templates/account/channel/perm` with code as the name of the file. !!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

    4xx - Profile Control
        401 - Control (self)
        402 - Control (member)
        403 - Create / Edit / Delete
    """

    @classmethod
    def default(cls):
        raise ProfilePermission.NORMAL

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

    PRF_CONTROL_SELF = \
        401, _("Profile: Control (self)"), \
        _("User who has this permission can attach/detach profile to themselves.")

    PRF_CONTROL_MEMBER = \
        402, _("Profile: Control (member)"), \
        _("User who has this permission can attach/detach profiles to the other members.")

    PRF_CED = \
        403, _("Profile: CED"), \
        _("User who has this permission can create / edit / delete (CED) profiles.")


class PermissionLevel(FlagSingleEnum):
    @classmethod
    def default(cls):
        return PermissionLevel.NORMAL

    @classmethod
    def lowest(cls):
        return PermissionLevel.NORMAL

    @classmethod
    def highest(cls):
        return PermissionLevel.ADMIN

    NORMAL = 0, _("Normal")
    MOD = 1, _("Moderator")
    ADMIN = 2, _("Admin")

    @property
    def iter_to_max(self) -> Generator['PermissionLevel', None, None]:
        # noinspection PyTypeChecker
        for i in list(self.__class__):
            yield i
            if i == self:
                return


class ProfilePermissionDefault:
    _Cache = {}

    _Default = {
        ProfilePermission.NORMAL
    }

    # noinspection PyTypeChecker
    _Override = {
        PermissionLevel.MOD: {
            ProfilePermission.AR_ACCESS_PINNED_MODULE
        },
        PermissionLevel.highest(): set(ProfilePermission)
    }

    @staticmethod
    def get_overridden_permissions(highest_perm_lv: PermissionLevel) -> Set[ProfilePermission]:
        if highest_perm_lv not in ProfilePermissionDefault._Cache:
            perms = ProfilePermissionDefault._Default
            for perm_lv in highest_perm_lv.iter_to_max:
                perms = perms.union(ProfilePermissionDefault._Override.get(perm_lv, set()))

            ProfilePermissionDefault._Cache[highest_perm_lv] = perms

        return ProfilePermissionDefault._Cache[highest_perm_lv]

    @staticmethod
    def get_default_dict() -> Dict[ProfilePermission, bool]:
        return {perm_cat: perm_cat in ProfilePermissionDefault._Default for perm_cat in ProfilePermission}

    @staticmethod
    def get_default_code_str_dict() -> Dict[str, bool]:
        return {k.code_str: v for k, v in ProfilePermissionDefault.get_default_dict().items()}
