from django.utils.translation import gettext_noop as _

from extutils.flags import FlagDoubleEnum


# DRAFT: Permission - Create default preset pool
class PermissionCategory(FlagDoubleEnum):
    @staticmethod
    def default():
        raise PermissionCategory.NORMAL

    NORMAL = \
        0, _("Normal"), \
        _("User who has this permission can do all normal operations.")

    AR_MODERATE_PINNED_MODULE = \
        101, _("Auto-Reply: Moderate Pinned Module"), \
        _("User who has this permission can access the Pinned property of the Auto-Reply modules.")

    MGR_CHANGE_MEMBERS = \
        201, _("Managers: Change Members"), \
        _("User who has this permission can change the members of managers.")
