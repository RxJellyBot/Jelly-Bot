"""String resources for :class:`extutils`."""
from django.utils.translation import gettext_lazy as _

__all__ = ("DateTime",)


# pylint: disable=too-few-public-methods


class DateTime:
    """String resources for :class:`extutils.dt`."""

    @staticmethod
    def get_time_expr(hours: int, minutes: int, seconds: int, days: int = None):
        """
        Get the time expression.

        If ``days`` are given and > 3, returned expression will be in the format of **dd Days hh H mm M ss S**.

        If ``days`` are either not given (being ``None``) or <= 3, returned expression will be in the format of
        **hhh H mm M ss S**.

        :param hours: hours in time
        :param minutes: minutes in time
        :param seconds: second in time
        :param days: days in time
        :return: formatted expression of the time
        """
        str_dict = {
            "d": days,
            "h": hours,
            "m": minutes,
            "s": seconds
        }

        if days:
            if days > 3:
                return _("%(d)d Days %(h)d H %(m)02d M %(s)02d S") % str_dict

            str_dict["h"] += days * 24

        return _("%(h)d H %(m)02d M %(s)02d S") % str_dict
