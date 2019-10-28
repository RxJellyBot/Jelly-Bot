from discord import Client, Activity, ActivityType

from flags import Platform
from extdiscord import handle_discord_main
from extdiscord.logger import DISCORD
from JellyBot.components.utils import load_server
from msghandle.models import MessageEventObjectFactory

from .token_ import discord_token

__all__ = ["run_server"]


class DiscordClient(Client):
    async def on_ready(self):
        DISCORD.logger.info(f"Logged on as {self.user}.")
        # Load server for possible reverse() call
        load_server()

        await self.change_presence(activity=Activity(name="8===D", type=ActivityType.playing))

    async def on_message(self, message):
        # Prevent self reading and bot resonate
        if message.author == self.user or message.author.bot:
            return

        DISCORD.logger.info(
            f"Author: {message.author} / Content: {message.content}")

        await handle_discord_main(
            MessageEventObjectFactory.from_discord(message)).to_platform(Platform.DISCORD).send_discord(message.channel)


def run_server():
    DiscordClient().run(discord_token)
