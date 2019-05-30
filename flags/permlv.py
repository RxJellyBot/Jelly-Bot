from django.utils.translation import gettext_noop as _

from extutils.flags import FlagDoubleEnum


# DRAFT: Permission -
class PermissionLevel(FlagDoubleEnum):
    @staticmethod
    def default():
        return PermissionLevel.NORMAL

    BLOCKED = \
        -2, _("Blocked"), \
        _("Blocked user will not be able to use ALL functions for a period of time.")
    SUPPRESSED = \
        -1, _("Suppressed"), \
        _("Suppressed user will not be able to use non-onsite functions for a period of time.")
    NORMAL = \
        0, _("Normal"), \
        _("Normal user can use functions which do not require permission.")
    MODERATOR = \
        2, _("Moderator"), \
        _("Moderator will gain extra access to some functions.")
    ADMIN = \
        3, _("Admin"), \
        _("Admin will do all what moderator can do and gain extra access to some functions.")
