"""Utils to get various information related to Discord channel."""
from typing import Union

from discord import Message, TextChannel, VoiceChannel, CategoryChannel


def msg_loc_repr(message: Message):
    """
    Get the channel location representation of where the message was sent.

    The representation format will be ``<GUILD_NAME>/<CHANNEL_NAME>``.

    If the channel is not being sent in a server, return ``<CHANNEL_NAME>`` instead.

    :param message: message to be analyzed
    :return: the location representation of where the message was sent
    """
    if message.guild:
        return f"{str(message.guild)} / {str(message.channel)}"

    return str(message.channel)


def channel_full_repr(channel: Union[TextChannel, VoiceChannel, CategoryChannel]):
    """
    Full representation of the ``channel`` in a server in the format of ``<GUILD_NAME>/<CHANNEL_NAME>``.

    :param channel: channel to get the representation
    :return: representation of the channel
    """
    return f"{str(channel.guild)} / {str(channel)}"
