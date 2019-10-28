from discord import Message


def channel_repr(message: Message):
    if message.guild:
        return f"{str(message.guild)} / {str(message.channel)}"
    else:
        return str(message.channel)
