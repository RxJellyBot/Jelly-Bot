from discord import Client

from .token_ import discord_token


class DiscordClient(Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}.")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.name.startswith("jbok"):
            print(f"Channel Name: {message.channel.name} / Author: {message.author} / Content: {message.content}")
            await message.channel.send(message.content)


def start_client():
    DiscordClient().run(discord_token)
