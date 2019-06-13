from django.utils.translation import gettext_noop as _

from extutils.flags import FlagDoubleEnum


class PermissionCategory(FlagDoubleEnum):
    @staticmethod
    def default():
        raise PermissionCategory.NORMAL

    NORMAL = \
        0, _("Normal"), \
        _("User who has this permission can do all normal operations.")

    AR_ACCESS_PINNED_MODULE = \
        101, _("Auto-Reply: Access Pinned Module"), \
        _("User who has this permission can access the Pinned property of the Auto-Reply modules.")

    MBR_CHANGE_MEMBERS = \
        201, _("Members: Change Managers"), \
        _("User who has this permission can change the members of managers.")
