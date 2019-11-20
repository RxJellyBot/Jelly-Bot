from django.utils.translation import gettext_lazy as _
from discord import ChannelType as DiscordChannelType

from extutils.flags import FlagSingleEnum

from .platforms import Platform


class ChannelTypeUnidentifiable(Exception):
    pass


class ChannelType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return ChannelType.UNKNOWN

    UNKNOWN = 0, _("(Unknown Channel Type)")
    GROUP_PUB_TEXT = 10, _("Group (Text/Public)")
    GROUP_PRV_TEXT = 11, _("Group (Text/Private)")
    PRIVATE_TEXT = 21, _("Private (Text)")

    @staticmethod
    def identify(platform, token: str):
        from extline import LineApiUtils

        if platform == Platform.LINE:
            return LineApiUtils.get_channel_type(token)
        else:
            raise ChannelTypeUnidentifiable()

    @staticmethod
    def trans_from_discord(ctype: DiscordChannelType):
        if ctype == DiscordChannelType.private:
            return ChannelType.PRIVATE_TEXT
        elif ctype == DiscordChannelType.group:
            return ChannelType.GROUP_PRV_TEXT
        elif ctype == DiscordChannelType.text:
            return ChannelType.GROUP_PUB_TEXT
        else:
            return ChannelType.UNKNOWN
