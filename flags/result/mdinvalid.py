from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum, FlagOutcomeMixin


class ModelValidityCheckResult(FlagOutcomeMixin, FlagDoubleEnum):
    """
    # SUCCESS

    -1 - OK

    ================================

    # FAILED

    1xx - Auto Reply
        10x - Content Validations
            101 - Empty content

            102 - Image validation dailed

            103 - LINE sticker validation failed

    2xx - Identity Managements
        20x - Root User
            201 - No related identity data

    3xx - Execode
        301 - Action type unknown

        302 - Data error

    9xx - Miscellaneous
        901 - Uncategorized

        902 - Error
    """
    @classmethod
    def default(cls):
        return ModelValidityCheckResult.O_OK

    O_OK = -1, _("O: OK"), _("The model is valid.")

    X_AR_CONTENT_EMPTY = \
        101, _("X: Auto Reply - Empty content"), \
        _("The content of the Auto-Reply is empty.")
    X_AR_CONTENT_NOT_IMAGE = \
        102, _("X: Auto Reply - Content not image"), \
        _("The content is not a pure image. Make sure that when you open the link in the browser, "
          "it gives you an image, NOT A WEB PAGE.")
    X_AR_CONTENT_NOT_LINE_STICKER = \
        103, _("X: Auto Reply - Content not LINE sticker"), \
        _("No sticker found using the sticker ID provided.")

    X_RTU_ALL_NONE = \
        201, _("X: Root User - No child IDs"), \
        _("No related identity data connected.")

    X_EXC_ACTION_UNKNOWN = \
        301, _("X: Execode - Unknown action"), \
        _("The Execode action type is unknown.")
    X_EXC_DATA_ERROR = \
        302, _("X: Execode - Data error"), \
        _("The data of the Execode action contains error.")

    X_UNCATEGORIZED = \
        901, _("X: Uncategorized Reason"), \
        _("Model is invalid for uncategorized reason.")
    X_ERROR = \
        902, _("X: Error"), \
        _("An error occurred during model validation.")
