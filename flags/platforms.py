"""
Flags for various platforms.

.. note::
    The module name **MUST** not be ``platform`` as it could potentially creates import problem.
"""
from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class Platform(FlagSingleEnum):
    """Supported platforms."""

    @classmethod
    def default(cls):
        return Platform.UNKNOWN

    UNKNOWN = 0, _("Unknown Platform")
    LINE = 1, _("LINE")
    DISCORD = 2, _("Discord")
