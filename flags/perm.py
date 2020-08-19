"""Flags related to bot configuring permission."""
from typing import Dict, Generator, Set, Optional

from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum, FlagSingleEnum


class ProfilePermission(FlagDoubleEnum):
    """
    Defined profile permissions.

    Currently defined permissions are:
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

    .. note::
        **ADD CORRESPONDING HTMl FILE UNDER ``templates/account/channel/perm`` WITH CODE AS THE NAME OF THE FILE.
    """

    @classmethod
    def default(cls):
        return ProfilePermission.NORMAL

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
    """Defined permission levels."""

    @classmethod
    def default(cls):
        return PermissionLevel.NORMAL

    @classmethod
    def lowest(cls):
        """Lowest permission level."""
        return PermissionLevel.NORMAL

    @classmethod
    def highest(cls):
        """Highest permission level."""
        return PermissionLevel.ADMIN

    NORMAL = 0, _("Normal")
    MOD = 1, _("Moderator")
    ADMIN = 2, _("Admin")

    @property
    def iter_to_max(self) -> Generator['PermissionLevel', None, None]:
        """
        Get a generator iterating from the lowest :class:`PermissionLevel` to the current :class:`PermissionLevel`.

        For example, :class:`PermissionLevel.MOD` yields
        :class:`PermissionLevel.NORMAL` and :class:`PermissionLevel.MOD`.
        """
        # noinspection PyTypeChecker
        for i in list(self.__class__):
            yield i
            if i == self:
                return


class ProfilePermissionDefault:
    """Get the default permission settings for the corresponding permission level."""

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
        """
        Get the permissions that have been overridden at the permission level ``highest_perm_lv``.

        :param highest_perm_lv: permission level to the get the overridden permissions
        :return: permissions overridden at `highest_perm_lv`
        """
        if highest_perm_lv not in ProfilePermissionDefault._Cache:
            perms = ProfilePermissionDefault._Default
            for perm_lv in highest_perm_lv.iter_to_max:
                perms = perms.union(ProfilePermissionDefault._Override.get(perm_lv, set()))

            ProfilePermissionDefault._Cache[highest_perm_lv] = perms

        return ProfilePermissionDefault._Cache[highest_perm_lv]

    @staticmethod
    def get_default_dict(addl_perm: Optional[Set[ProfilePermission]] = None) -> Dict[ProfilePermission, bool]:
        """
        Get the default permissions at :class:`PermissionLevel.NORMAL` plus the permissions in ``addl_perm``.

        Each value of the returned :class:`dict` indicates
        if its corresponding :class:`ProfilePermission` (key) is available.

        :param addl_perm: additional permissions to be added in the returned `dict`
        :return: enabled permissions by default with `addl_perm`
        """
        ret = {perm_cat: perm_cat in ProfilePermissionDefault._Default for perm_cat in ProfilePermission}

        if addl_perm:
            for perm in addl_perm:
                ret[perm] = True

        return ret

    @staticmethod
    def get_default_code_str_dict(addl_perm: Optional[Set[ProfilePermission]] = None) -> Dict[str, bool]:
        """
        Get the result of ``get_default_dict()`` but the keys become ``code_str`` for each :class:`ProfilePermission`.

        :param addl_perm: additional permissions to be added in the returned `dict`
        :return: enabled permissions by default with `addl_perm`
        """
        return {k.code_str: v for k, v in ProfilePermissionDefault.get_default_dict(addl_perm).items()}
