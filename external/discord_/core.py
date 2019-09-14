from discord import Client, Activity, ActivityType
from external.discord_.logger import DISCORD
from external.handle import EventObjectFactory, handle_main

from .token_ import discord_token


class DiscordClient(Client):
    async def on_ready(self):
        DISCORD.logger.info(f"Logged on as {self.user}.")
        await self.change_presence(activity=Activity(name="the sky", type=ActivityType.watching))

    async def on_message(self, message):
        # Prevent self reading
        if message.author == self.user or message.author.bot:
            return

        if message.channel.name.startswith("jbok"):
            # FIXME: [LP] handle returned type will be changed
            DISCORD.logger.info(
                f"Channel Name: {message.channel.name} / Author: {message.author} / Content: {message.content}")
            await message.channel.send(handle_main(EventObjectFactory.from_discord(message)))


def start_client():
    DiscordClient().run(discord_token)
