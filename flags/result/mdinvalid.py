from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum


class ModelValidityCheckResult(FlagDoubleEnum):
    """
    # SUCCESS

    -1 - OK

    ================================

    # FAILED

    1xx - Auto Reply
        10x - Content Validations
            101 - Empty Content
            102 - Image Validation Failed
            103 - LINE Sticker Validation Failed

    2xx - Identity Managements
        20x - Root User
            201 - No related identity data

    9xx - Miscellaneous
        901 - Uncategorized
    """
    @classmethod
    def default(cls):
        return ModelValidityCheckResult.O_OK

    O_OK = -1, _("O: OK"), _("The model is valid.")

    X_AR_CONTENT_EMPTY = \
        101, _("X: Auto Reply - Empty Content"), \
        _("The content of the Auto-Reply is empty.")
    X_AR_CONTENT_NOT_IMAGE = \
        102, _("X: Auto Reply - Content not Image"), \
        _("The content is not a pure image. Make sure that when you open the link in the browser, "
          "it gives you an image, NOT A WEB PAGE.")
    X_AR_CONTENT_NOT_LINE_STICKER = \
        103, _("X: Auto Reply - Content not LINE Sticker"), \
        _("No sticker found using the sticker ID provided.")

    X_RTU_ALL_NONE = \
        201, _("X: Root User - No child IDs"), \
        _("No related identity data connected.")

    X_UNCATEGORIZED = 901, _("X: Uncategorized Reason"), _("Model is invalid for uncategorized reason.")

    def is_success(self):
        return self.code < 0
