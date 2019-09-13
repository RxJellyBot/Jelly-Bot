from discord import Client
from external.discord_.logger import DISCORD

from .token_ import discord_token


class DiscordClient(Client):
    async def on_ready(self):
        DISCORD.logger.info(f"Logged on as {self.user}.")

    async def on_message(self, message):
        if message.author == self.user or message.author.bot:
            return

        if message.channel.name.startswith("jbok"):
            DISCORD.logger.info(f"Channel Name: {message.channel.name} / Author: {message.author} / Content: {message.content}")
            await message.channel.send(message.content)


def start_client():
    DiscordClient().run(discord_token)
