from discord import Client

from .token import discord_token


class DiscordClient(Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, message):
        if message.author == client.user:
            return

        print(f"Message Author: {message.author} / Content: {message.content}")
        message.channel.send(message.content)


client = DiscordClient()
client.run(discord_token)
