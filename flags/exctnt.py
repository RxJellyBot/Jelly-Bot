from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class ExtraContentType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return ExtraContentType.PURE_TEXT

    PURE_TEXT = 0, _("Pure Text")
