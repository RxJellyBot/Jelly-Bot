"""
Contains the flag of various platforms.

.. note::
    The name **MUST** not be ``platform`` as it could potentially creates import problem.
"""
from django.utils.translation import gettext_lazy as _

from rxtoolbox.flags import FlagSingleEnum


class Platform(FlagSingleEnum):
    @classmethod
    def default(cls):
        return Platform.UNKNOWN

    UNKNOWN = 0, _("Unknown Platform")
    LINE = 1, _("LINE")
    DISCORD = 2, _("Discord")
