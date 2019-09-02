from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class Platform(FlagSingleEnum):
    @classmethod
    def default(cls):
        return Platform.UNKNOWN

    UNKNOWN = 0, _("Unknown Platform")
    LINE = 1, _("LINE")
    DISCORD = 2, _("Discord")
