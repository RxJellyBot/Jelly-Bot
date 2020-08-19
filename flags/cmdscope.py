"""Module for command scope flags."""
from dataclasses import dataclass, field
from typing import List

from django.utils.translation import gettext_lazy as _

from .chtype import ChannelType


@dataclass
class CommandScope:
    """Class representing the scope for the bot commands."""

    name: str

    # default value of an empty list means not restricted
    available_ctypes: List[ChannelType] = field(default_factory=list)

    def __post_init__(self):
        # If not restricted, fill all channel types
        if not self.available_ctypes:
            self.available_ctypes = list(ChannelType)

    def is_in_scope(self, ctype: ChannelType) -> bool:
        """
        Check if the given channel type is in the scope.

        :param ctype: channel type to be checked
        :return: if the given channel type is in the scope
        """
        if not self.available_ctypes:
            return True

        return ctype in self.available_ctypes

    @property
    def channel_type_repr(self) -> str:
        """
        Get the representation of the valid channel types of this scope.

        :return: representation of the valid channel types
        """
        return ' / '.join([str(ctype.key) for ctype in self.available_ctypes])


class CommandScopeCollection:
    """Defined available command scopes to be used."""

    # pylint: disable=too-few-public-methods

    NOT_RESTRICTED = CommandScope(_("Not Restricted"))
    GROUP_ONLY = CommandScope(_("Group Only"), [ChannelType.GROUP_PUB_TEXT, ChannelType.GROUP_PRV_TEXT])
    PRIVATE_ONLY = CommandScope(_("Private Only"), [ChannelType.PRIVATE_TEXT])
