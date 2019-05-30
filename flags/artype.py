from django.utils.translation import gettext_noop as _

from extutils.flags import FlagSingleEnum


class AutoReplyContentType(FlagSingleEnum):
    @staticmethod
    def default():
        return AutoReplyContentType.TEXT

    CUSTOM_SIG = -1, _("Custom Signal")
    TEXT = 0, _("Text")
    IMAGE = 1, _("Image")
    LINE_STICKER = 2, _("Image")
