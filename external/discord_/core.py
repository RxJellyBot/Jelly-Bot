import threading

from discord import Client, Activity, ActivityType

from external.discord_.logger import DISCORD
from external.handle import EventObjectFactory, handle_main
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

        if "test" in message.channel.name:
            # FIXME: [LP] Redirect to webpage if too long
            DISCORD.logger.info(
                f"Channel Name: {message.channel.name} / Author: {message.author} / Content: {message.content}")

            for txt_handled in handle_main(EventObjectFactory.from_discord(message)):
                await message.channel.send(txt_handled.content)


def run_server():
    """Non-blocking server activation call."""
    threading.Thread(target=DiscordClient().run, args=(discord_token,)).start()
