from django.utils.translation import gettext_lazy as _

from rxtoolbox.flags import FlagSingleEnum


class APICommand(FlagSingleEnum):
    """
    1xx - Auto Reply:
        10x - Main Functions:
            101: Add
        11x - Side Functions:
            111: Content Vaidation
        12x - Tag controls:
            121: Query Tag Popularity

    2xx - Execode:
        20x - Auto reply:
            201: Complete Addition

        29x - Miscellaneous
            291: List all Execode
            299: Complete Action

    3xx - Data Query:
        30x - Identity:
            301: Channel Data
            302: Permission

    4xx - Management
        40x - Channel
            401: Issue Channel Registration Execode
            402: Change Channel Star
            403: Change Channel Name
        41x - Profile
            411: Detach
            412: Check Name
            413: Attach

    5xx - Special Services
        50x - Short URL
            501: Shorten URL
            502: Update Target
    """
    @classmethod
    def default(cls):
        return APICommand.UNKNOWN

    UNKNOWN = -1, _("Unknown Action")

    AR_ADD = 101, _("Auto-Reply - Addition")
    AR_CONTENT_VALIDATE = 111, _("Auto-Reply - Content Validation")
    AR_TAG_POP = 121, _("Auto-Reply - Tag Popularity")

    EXECODE_AR_ADD = 201, _("Execode - Auto-Reply Addition")
    EXECODE_LIST = 291, _("Execode - List All")
    EXECODE_COMPLETE = 299, _("Execode - Complete Action")

    DATA_CHANNEL = 301, _("Data Query - Channel")
    DATA_PERMISSION = 302, _("Data Query - Permission")

    MG_CHANNEL_ISSUE_REG = 401, _("Management - Issue Channel Registration Execode")
    MG_CHANNEL_STAR_CHANGE = 402, _("Management - Change Channel Star")
    MG_CHANNEL_NAME_CHANGE = 403, _("Management - Change Channel Name")

    MG_PROFILE_DETACH = 411, _("Management - Detach Profile")
    MG_PROFILE_NAME_CHECK = 412, _("Management - Profile Name Check")
    MG_PROFILE_ATTACH = 413, _("Management - Attach Profile")

    SERV_SHORTEN_URL = 501, _("Services - Shorten URL")
    SERV_UPDATE_TARGET = 502, _("Services - Update Target")
