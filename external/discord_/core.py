from discord import Client, Activity, ActivityType
from external.discord_.logger import DISCORD
# FIXME: [HP] Get rid of this or make it lazy
# from external.handle import EventObjectFactory, handle_main

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
            # FIXME: [LP] Redirect to webpage if too long
            DISCORD.logger.info(
                f"Channel Name: {message.channel.name} / Author: {message.author} / Content: {message.content}")

            # for txt_handled in handle_main(EventObjectFactory.from_discord(message)):
            #     await message.channel.send(txt_handled.content)
            await message.channel.send(message.content)


def start_client():
    DiscordClient().run(discord_token)
