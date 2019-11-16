from dataclasses import dataclass, field
from typing import List

from django.utils.translation import gettext_lazy as _

from .chtype import ChannelType


@dataclass
class CommandScope:
    name: str
    available_ctypes: List[ChannelType] = field(default_factory=list)  # default value of `list` means not restricted

    def __post_init__(self):
        # If not restricted, fill all channel types
        if not self.available_ctypes:
            self.available_ctypes = [c for c in ChannelType]

    def is_in_scope(self, ctype: ChannelType):
        if not self.available_ctypes:
            return True

        return ctype in self.available_ctypes

    @property
    def list_channel_str(self) -> str:
        return ' / '.join([str(ctype.key) for ctype in self.available_ctypes])


class CommandScopeCollection:
    NOT_RESTRICTED = CommandScope(_("Not Restricted"))
    GROUP_ONLY = CommandScope(_("Group Only"), [ChannelType.GROUP_PUB_TEXT, ChannelType.GROUP_PRV_TEXT])
    PRIVATE_ONLY = CommandScope(_("Private Only"), [ChannelType.PRIVATE_TEXT])
