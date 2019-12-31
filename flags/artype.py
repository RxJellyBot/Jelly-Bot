from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class AutoReplyContentType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return AutoReplyContentType.TEXT
    TEXT = 0, _("Text")
    IMAGE = 1, _("Image")
    LINE_STICKER = 2, _("LINE Sticker")

    CUSTOM_SIG = -1, _("Custom Signal")

    @staticmethod
    def determine(content: str):
        # LINE API requires image to be sent in HTTPS protocol
        if content.endswith(".jpg") and content.startswith("https://"):
            return AutoReplyContentType.IMAGE
        elif content.isnumeric():
            return AutoReplyContentType.LINE_STICKER
        else:
            return AutoReplyContentType.TEXT
