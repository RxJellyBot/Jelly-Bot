"""Module for message type flags."""
from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class MessageType(FlagSingleEnum):
    """Supported message types."""

    @classmethod
    def default(cls):
        return MessageType.UNKNOWN

    UNKNOWN = 0, _("Unknown")
    TEXT = 1, _("Text")
    IMAGE = 2, _("Image")
    VIDEO = 3, _("Video")
    AUDIO = 4, _("Audio")
    LOCATION = 5, _("Location")
    LINE_STICKER = 6, _("Sticker")
    FILE = 7, _("File")
