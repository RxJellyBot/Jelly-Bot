from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class APIAction(FlagSingleEnum):
    """
    1xx - Auto Reply:
        10x - Main Functions:
            101: Add
        11x - Side Functions:
            111: Content Vaidation

    2xx - Token Action:
        20x - Auto reply:
            201: Complete Addition

        29x - Miscellaneous
            291: List all token actions
            299: Complete Action

    3xx - Data Query:
        30x - Identity:
            301: Channel Data

    4xx - Management
        40x - Channel
            401: Issue Channel Registration Token
            402: Complete Channel Registration
    """
    @classmethod
    def default(cls):
        return APIAction.UNKNOWN

    UNKNOWN = -1, _("Unknown Action")

    AR_ADD = 101, _("Auto-Reply Addition")
    AR_CONTENT_VALIDATE = 111, _("Auto-Reply Content Validation")

    TOKEN_AR_ADD = 201, _("Token Action - Auto-Reply Addition")
    TOKEN_LIST = 291, _("Token Action - List All")
    TOKEN_COMPLETE = 299, _("Token Action - Complete Action")

    DATA_CHANNEL = 301, _("Data Query - Channel")

    MG_CHANNEL_ISSUE_REG = 401, _("Management - Issue Channel Registration Token")
