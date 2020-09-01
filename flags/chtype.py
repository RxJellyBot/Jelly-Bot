"""Module for channel type flags."""
from django.utils.translation import gettext_lazy as _
from discord import ChannelType as DiscordChannelType

from extutils.flags import FlagSingleEnum

from .platforms import Platform


class ChannelTypeUnidentifiableError(Exception):
    """Raised if the channel type is unidentifiable."""


class ChannelType(FlagSingleEnum):
    """Supported channel type flags for the bot."""

    @classmethod
    def default(cls):
        return ChannelType.UNKNOWN

    UNKNOWN = 0, _("(Unknown Channel Type)")
    GROUP_PUB_TEXT = 10, _("Group (Text/Public)")
    GROUP_PRV_TEXT = 11, _("Group (Text/Private)")
    PRIVATE_TEXT = 21, _("Private (Text)")

    @staticmethod
    def identify(platform, token: str) -> 'ChannelType':
        """
        Identify the channel type using ``platform`` and ``token``.

        Currently only supports LINE with token.

        :param platform: source platform of the token
        :param token: token for the channel to be identified
        :return: type of the channel
        :raises ChannelTypeUnidentifiableError: if the channel type cannot be identified
        """
        # To prevent looped import
        from extline import LineApiUtils  # pylint: disable=import-outside-toplevel

        if platform == Platform.LINE:
            return LineApiUtils.get_channel_type(token)

        raise ChannelTypeUnidentifiableError()

    @staticmethod
    def convert_from_discord(ctype: DiscordChannelType) -> 'ChannelType':
        """
        Convert :class:`DiscordChannelType` for ``discord.py`` to :class:`ChannelType`.

        :param ctype: `DiscordChannelType` to be converted
        :return: converted channel type for the bot
        """
        if ctype == DiscordChannelType.private:
            return ChannelType.PRIVATE_TEXT

        if ctype == DiscordChannelType.group:
            return ChannelType.GROUP_PRV_TEXT

        if ctype == DiscordChannelType.text:
            return ChannelType.GROUP_PUB_TEXT

        return ChannelType.UNKNOWN
