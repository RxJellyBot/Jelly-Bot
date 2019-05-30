from django.utils.translation import gettext_noop as _

from extutils.flags import FlagSingleEnum


class TokenAction(FlagSingleEnum):
    """
    1xx - Identity Management:
        10x - Connect IDs:
            101: Connect API to OnPlat (Use token on site to complete connection)
            102: Connect OnPlat to API (Use token on any platform to complete connection)

    20x - Auto Reply:
            201: Add
    """
    @staticmethod
    def default():
        return TokenAction.UNKNOWN

    UNKNOWN = -1, _("Unknown token action")

    CONNECT_API_TO_ONPLAT = 101, _("API -> OnPlat")
    CONNECT_ONPLAT_TO_API = 102, _("OnPlat -> API")

    AR_ADD = 201, _("Auto-Reply Addition")
