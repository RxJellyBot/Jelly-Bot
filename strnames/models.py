from django.utils.translation import gettext_lazy as _

__all__ = ["StatsResults", "Timer"]


class StatsResults:
    CATEGORY_TOTAL = _("(Total)")

    DAYS_MEAN = _("{} days mean")

    COUNT_BEFORE = _("Message Count Before {}")


class Timer:
    PAST_CONTINUE = _("- [{diff}] past {event} (at {time})")
    PAST_DONE = _("- {event} has ended (at {time})")
    FUTURE = _("- [{diff}] to {event} (at {time})")
