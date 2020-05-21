from django.utils.translation import gettext_lazy as _

__all__ = ["StatsResults"]


class StatsResults:
    CATEGORY_TOTAL = _("(Total)")

    DAYS_MEAN = _("{} days mean")

    COUNT_BEFORE = _("Message Count Before {}")
