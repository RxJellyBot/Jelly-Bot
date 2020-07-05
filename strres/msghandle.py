from django.utils.translation import gettext_lazy as _

__all__ = ["ToSiteReason", "Event", "HandledResult"]


class HandledResult:
    ErrorHandle = _("An error occurred while handling message. An error report was sent for investigation.")

    TestFailedNoToken = "No user token handling point reached"

    TestSuccessImage = "Image message handling point reached"
    TestSuccessLineSticker = "Sticker message handling point reached"


class Event:
    TestRaw = "(Test Raw Event)"
    TestUserToken = "(Test User Token)"


class ToSiteReason:
    TOO_LONG = _("Message length overlimit")
    TOO_MANY_RESPONSES = _("Responses length overlimit")
    TOO_MANY_LINES = _("Too many lines")
    LATEX_AVAILABLE = _("LaTeX available")
    FORCED_ONSITE = _("Content was forced to be displayed on the website")
