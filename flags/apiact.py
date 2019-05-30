from django.utils.translation import gettext_noop as _

from extutils.flags import FlagSingleEnum


class APIAction(FlagSingleEnum):
    """
    1xx - Auto Reply:
            101: Add
    2xx - Token Action:
        20x - Auto reply:
            201: Complete Addition
    """
    @staticmethod
    def default():
        return APIAction.UNKNOWN

    UNKNOWN = -1, _("Unknown Action")

    AR_ADD = 101, _("Auto-Reply Addition")

    TOKEN_AR_ADD = 201, _("Token Action - Auto-Reply Addition")
