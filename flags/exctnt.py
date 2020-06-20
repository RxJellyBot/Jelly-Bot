from django.utils.translation import gettext_lazy as _

from rxtoolbox.flags import FlagSingleEnum


class ExtraContentType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return ExtraContentType.PURE_TEXT

    PURE_TEXT = 0, _("Pure Text")
    EXTRA_MESSAGE = 1, _("Extra Message")

    AUTO_REPLY_SEARCH = 100, _("Auto Reply Search Result")
