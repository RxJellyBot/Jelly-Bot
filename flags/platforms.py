from django.utils.translation import gettext_noop as _

from extutils.flags import FlagSingleEnum


class Platform(FlagSingleEnum):
    @staticmethod
    def default():
        return Platform.UNKNOWN

    UNKNOWN = 0, _("Unknown Platform")
    LINE = 1, _("LINE")
    DISCORD = 2, _("Discord")
