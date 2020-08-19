"""Module for Auto-Reply content type flag."""
from django.utils.translation import gettext_lazy as _

from extutils.imgproc import ImageValidator
from extutils.flags import FlagSingleEnum


class AutoReplyContentType(FlagSingleEnum):
    """Various defined auto-reply content type."""

    @classmethod
    def default(cls):
        return AutoReplyContentType.TEXT

    TEXT = 0, _("Text")
    IMAGE = 1, _("Image")
    LINE_STICKER = 2, _("LINE Sticker")

    CUSTOM_SIG = -1, _("Custom Signal")

    @staticmethod
    def determine(content: str):
        """
        Determine to content type of ``content``.

        :param content: content to determine the type
        :return: type of `content`
        """
        # LINE API requires image to be sent using HTTPS protocol
        image_ext_ok = ImageValidator.is_valid_image_extension(content)

        if image_ext_ok and content.startswith("https://"):
            return AutoReplyContentType.IMAGE

        if content.isnumeric():
            return AutoReplyContentType.LINE_STICKER

        return AutoReplyContentType.TEXT
