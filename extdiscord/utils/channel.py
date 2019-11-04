from typing import Union

from discord import Message, TextChannel, VoiceChannel, CategoryChannel


def msg_loc_repr(message: Message):
    if message.guild:
        return f"{str(message.guild)} / {str(message.channel)}"
    else:
        return str(message.channel)


def channel_full_repr(channel: Union[TextChannel, VoiceChannel, CategoryChannel]):
    return f"{str(channel.guild)} / {str(channel)}"
