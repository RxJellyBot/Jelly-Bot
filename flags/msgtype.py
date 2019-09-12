from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class MessageType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return MessageType.UNKNOWN

    UNKNOWN = 0, _("Unknown")
    TEXT = 1, _("Text")
