from django.utils.translation import gettext_lazy as _

__all__ = ["ToSiteReason"]


class ToSiteReason:
    TOO_LONG = _("Message length overlimit")
    TOO_MANY_RESPONSES = _("Responses length overlimit")
    TOO_MANY_LINES = _("Too many lines")
    LATEX_AVAILABLE = _("LaTeX available")
    FORCED_ONSITE = _("Content was forced to be displayed on the website")
