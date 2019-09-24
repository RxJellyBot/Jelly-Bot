from discord import Client, Activity, ActivityType
from django.test import RequestFactory

from flags import Platform
from external.discord_.logger import DISCORD
from external.discord_ import handle_discord_main
from external.handle import EventObjectFactory
from .token_ import discord_token

__all__ = ["run_server"]


class DiscordClient(Client):
    async def on_ready(self):
        DISCORD.logger.info(f"Logged on as {self.user}.")
        await self.change_presence(activity=Activity(name="8===D", type=ActivityType.playing))

    async def on_message(self, message):
        # Prevent self reading
        if message.author == self.user or message.author.bot:
            return

        # Create dummy request
        dummy_req = RequestFactory().get("/")

        if "test" in message.channel.name:
            DISCORD.logger.info(
                f"Channel Name: {message.channel.name} / Author: {message.author} / Content: {message.content}")

            handled_event = handle_discord_main(
                EventObjectFactory.from_discord(message)).to_platform(dummy_req, Platform.DISCORD)
            handled_event.push_content()

            for content in handled_event.to_send:
                await message.channel.send(content)


def run_server():
    DiscordClient().run(discord_token)
