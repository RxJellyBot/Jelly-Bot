from django.utils.translation import gettext_noop as _

from extutils.flags import FlagDoubleEnum


class PreserializationFailedReason(FlagDoubleEnum):
    """
    1xx - AutoReply
        10x - Content Serializing
            101 - Empty Content
            102 - Image Validation Failed
            103 - LINE Sticker Validation Failed
    """
    @staticmethod
    def default():
        return PreserializationFailedReason.UNKNOWN

    UNKNOWN = 0, _("Unknown Reason"), _("Preserialization process failed with unknown reason.")

    AR_CONTENT_EMPTY = \
        101, _("Auto Reply - Empty Content"), \
        _("The content of the Auto-Reply is empty.")
    AR_CONTENT_NOT_IMAGE = \
        102, _("Auto Reply - Content not Image"), \
        _("The content is not a pure image. Make sure that when you open the link in the browser, "
          "it gives you an image, NOT A WEB PAGE.")
    AR_CONTENT_NOT_LINE_STICKER = \
        103, _("Auto Reply - Content not LINE Sticker"), \
        _("No sticker found using the sticker ID provided.")
