"""Core objects for direct control on the Discord bot."""
import asyncio
from typing import Optional, Union
import threading

from django.utils.translation import gettext_lazy as _

from discord import (
    Client, Member, Guild, ChannelType,
    GroupChannel, DMChannel, TextChannel, VoiceChannel, CategoryChannel,
    Activity, ActivityType)

from bot.event import signal_discord_ready
from extdiscord.utils import channel_full_repr
from extdiscord.handle import handle_discord_main
from extdiscord.logger import DISCORD
from extutils.checker import arg_type_ensure
from extutils.emailutils import MailSender
from flags import Platform
from mongodb.factory import ChannelManager, ChannelCollectionManager, RootUserManager, ProfileManager
from msghandle.models import MessageEventObjectFactory

from .token_ import discord_token
from .utils.cnflprvt import BotConflictionPreventer

__all__ = ("run_server", "DiscordClientWrapper",)


class DiscordClient(Client):
    """
    Discord bot client. This is the main class of the discord bot event handler.

    .. seealso::
        Discord bot events: https://discordpy.readthedocs.io/en/latest/api.html#event-reference
    """

    async def on_ready(self):
        """Contains the code to be executed when the bot is ready."""
        # Not importing at the top level because the app will not be ready yet (translation unavailable)
        from msghandle.botcmd.command import cmd_help  # pylint: disable=import-outside-toplevel

        DISCORD.logger.info("Logged in as %s.", self.user)

        BotConflictionPreventer.initialize(self.user.id)
        signal_discord_ready()

        await self.change_presence(activity=Activity(name=cmd_help.get_usage(), type=ActivityType.watching))

    async def on_message(self, message):
        """Contains the code to be executed when a message is being received."""
        # Prevent self reading and bots to resonate
        if message.author == self.user \
                or message.author.bot \
                or BotConflictionPreventer.prioritized_bot_exists(message.guild):
            return

        await handle_discord_main(MessageEventObjectFactory.from_discord(message)) \
            .to_platform(Platform.DISCORD) \
            .send_discord(message.channel)

    # noinspection PyMethodMayBeStatic
    async def on_private_channel_delete(self, channel: Union[DMChannel, GroupChannel]):
        """Contains the code to be executed when a private channel is deleted."""
        outcome = ChannelManager.deregister(Platform.DISCORD, channel.id)

        if not outcome.is_success:
            warn_txt = f"Private channel DELETED but the deregistration was failed.\n" \
                       f"Channel token: {channel.id}\n" \
                       f"Outcome: {outcome}"
            DISCORD.logger.warning(warn_txt)
            MailSender.send_email_async(warn_txt, subject="Discord private channel deletion failed")

    # noinspection PyMethodMayBeStatic
    async def on_private_channel_create(self, channel: Union[DMChannel, GroupChannel]):
        """Contains the code to be executed when a private channel is created."""
        outcome = ChannelManager.ensure_register(Platform.DISCORD, channel.id, default_name=str(channel))

        if not outcome.success:
            warn_txt = f"Private channel CREATED but the registration was failed.\n" \
                       f"Channel token: {channel.id}\n" \
                       f"Outcome: {outcome}"
            DISCORD.logger.warning(warn_txt)
            MailSender.send_email_async(warn_txt, subject="Discord private channel creation failed")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    async def on_private_channel_update(self, before: GroupChannel, after: GroupChannel):
        """Contains the code to be executed when the info of a private channel is updated."""
        if str(before) != str(after):
            outcome = ChannelManager.update_channel_default_name(Platform.DISCORD, after.id, str(after))

            if not outcome.is_success:
                warn_txt = f"Private channel name UPDATED but the name was not updated.\n" \
                           f"Channel token: {after.id}\n" \
                           f"Name: {str(before)} to {str(after)}\n" \
                           f"Outcome: {outcome}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord private channel name update failed")

    # noinspection PyMethodMayBeStatic
    async def on_guild_channel_delete(self, channel: Union[TextChannel, VoiceChannel, CategoryChannel]):
        """Contains the code to be executed when a channel of a Discord server is deleted."""
        if channel.type == ChannelType.text:
            outcome = ChannelManager.deregister(Platform.DISCORD, channel.id)

            if not outcome.is_success:
                warn_txt = f"Guild channel DELETED but the deregistration was failed.\n" \
                           f"Channel token: {channel.id}\n" \
                           f"Outcome: {outcome}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord guild channel deletion failed")

    # noinspection PyMethodMayBeStatic
    async def on_guild_channel_create(self, channel: Union[TextChannel, VoiceChannel, CategoryChannel]):
        """Contains the code to be executed when a channel of a Discord server is created."""
        if channel.type == ChannelType.text:
            reg_result = ChannelManager.ensure_register(
                Platform.DISCORD, channel.id, default_name=channel_full_repr(channel))

            if not reg_result.success:
                warn_txt = f"Guild channel CREATED but the registration was failed.\n" \
                           f"Channel token: {channel.id}\n" \
                           f"Outcome: {reg_result.outcome}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord guild channel creation failed")

            reg_result = ChannelCollectionManager.ensure_register(
                Platform.DISCORD, channel.guild.id, reg_result.model.id, default_name=str(channel.guild))

            if not reg_result.success:
                warn_txt = f"Guild channel CREATED but the collection registration was failed. " \
                           f"Channel token: {channel.id}\n" \
                           f"Outcome: {reg_result.outcome}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord channel collection creation failed")

    # noinspection PyMethodMayBeStatic
    async def on_guild_channel_update(
            self,
            before: Union[TextChannel, VoiceChannel, CategoryChannel],
            after: Union[TextChannel, VoiceChannel, CategoryChannel]):
        """Contains the code to be executed when the info of a channel of a Discord server is updated."""
        if str(before) != str(after):
            outcome = ChannelCollectionManager.update_default_name(
                Platform.DISCORD, after.guild.id, channel_full_repr(after))

            if not outcome.is_success:
                warn_txt = f"Guild channel name UPDATED but the name was not updated. " \
                           f"Channel token: {after.id}\n" \
                           f"Outcome: {outcome}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord guild channel name update failed")

    # noinspection PyMethodMayBeStatic
    async def on_member_join(self, member: Member):
        """Contains the code to be executed when a member joined a channel."""
        udata_result = RootUserManager.get_root_data_onplat(Platform.DISCORD, member.id, auto_register=True)
        cdata = ChannelManager.get_channel_token(Platform.DISCORD, member.guild.id, auto_register=True)

        if udata_result.success and cdata:
            ProfileManager.register_new_default_async(cdata.id, udata_result.model.id)

        sys_channel = member.guild.system_channel
        if sys_channel:
            await sys_channel.send(_("%s joined the server.") % member.mention)

    # noinspection PyMethodMayBeStatic
    async def on_member_remove(self, member: Member):
        """Contains the code to be executed when a member left a channel."""
        udata_result = RootUserManager.get_root_data_onplat(Platform.DISCORD, member.id, auto_register=True)
        cdata = ChannelManager.get_channel_token(Platform.DISCORD, member.guild.id, auto_register=True)

        if udata_result.success and cdata:
            ProfileManager.mark_unavailable_async(cdata.id, udata_result.model.id)

        sys_channel = member.guild.system_channel
        if sys_channel:
            await sys_channel.send(_("%s left the server.") % member.mention)

    # Other available hooks:
    #   on_guild_join(self, guild: Guild) -> bot joined a server
    #   on_guild_remove(self, guild: Guild) -> bot can no longer reach a server
    #   on_group_join(self, channel: GroupChannel, user: User) -> bot joined a group
    #   on_group_remove(self, channel: GroupChannel, user: User) -> bot can no longer reach a group


class _DiscordClientWrapper:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._core = DiscordClient(loop=self._loop)
        self._thread = None

    def run(self, token):
        """
        Blocking call to run the discord client.

        :param token: Discord bot token

        .. seealso::
            ``Client.run()``
        """
        self._core.run(token)

    def start_async(self):
        """
        Start the bot asynchronously by creating a thread and run it if not yet run.

        Nothing happens or changes if the bot is already running.
        """
        if not self._thread:
            self._thread = threading.Thread(
                target=DiscordClientWrapper.discord_loop.run_until_complete,
                args=(DiscordClientWrapper.start(discord_token),))
            self._thread.start()

    async def start(self, token):
        """
        Non-blocking call to run the discord client using ``async`` and ``await``.

        Returns a coroutine.

        :param token: Discord bot token

        .. seealso::
            ``Client.start()``
        """
        await self._core.start(token)

    @arg_type_ensure
    def get_user_name_safe(self, uid: int) -> Optional[str]:
        """
        Get the user name by providing the uid safely (Should not fail if not found).

        :param uid: Discord user id
        :return: the name of the user. `None` if not found.
        """
        udata = self._core.get_user(uid)

        if udata:
            return str(udata)

        return None

    @arg_type_ensure
    def get_guild(self, gid: int) -> Optional[Guild]:
        """
        Get the guild/server object by providing the gid.

        :param gid: Discord guild/server id
        :return: guild object if available
        """
        return self._core.get_guild(gid)

    def latency(self) -> float:
        """
        Get the bot connection latency.

        :return: connection latency in milliseconds
        """
        return self._core.latency

    @property
    def discord_client(self):
        """Discord bot client object."""
        return self._core

    @property
    def discord_loop(self):
        """The :class:`asyncio` loop in which the discord bot client is running."""
        return self._loop


DiscordClientWrapper = _DiscordClientWrapper()


def run_server():
    """
    Start the discord bot.

    .. note::
        Obtained from https://github.com/Rapptz/discord.py/issues/710#issuecomment-395609297
    """
    DiscordClientWrapper.start_async()
