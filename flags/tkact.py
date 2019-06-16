from django.utils.translation import gettext_noop as _

from extutils.flags import FlagSingleEnum, FlagDoubleEnum


class TokenAction(FlagSingleEnum):
    """
    1xx - Identity Management:
        10x - Connect IDs:
            101: Connect API to OnPlat (Use token on site to complete connection)
            102: Connect OnPlat to API (Use token on any platform to complete connection)

    20x - Auto Reply:
            201: Add
    """
    # TODO: Token Action - Possibly need to know complete OnPlat or OnSite
    @staticmethod
    def default():
        return TokenAction.UNKNOWN

    UNKNOWN = -1, _("Unknown")

    CONNECT_API_TO_ONPLAT = 101, _("API -> OnPlat")
    CONNECT_ONPLAT_TO_API = 102, _("OnPlat -> API")

    AR_ADD = 201, _("Auto-Reply Addition")


class TokenActionCollationErrorCode(FlagDoubleEnum):
    @staticmethod
    def default():
        return TokenActionCollationErrorCode.MISC

    MISC = -1, _("Error - Miscellaneous"), _("Miscellaneous collation error occurred.")

    EMPTY_CONTENT = 101, _("Empty Content"), _("The content is empty.")
