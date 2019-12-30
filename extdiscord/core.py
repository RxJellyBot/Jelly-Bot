import asyncio
from typing import Optional, Union
import threading

from discord import (
    Client, Member, User, Guild, ChannelType,
    GroupChannel, DMChannel, TextChannel, VoiceChannel, CategoryChannel,
    Activity, ActivityType)

from bot.event import signal_discord_ready
from extdiscord.utils import channel_full_repr
from extutils.checker import param_type_ensure
from extutils.emailutils import MailSender
from flags import Platform
from extdiscord import handle_discord_main
from extdiscord.logger import DISCORD
from mongodb.factory import ChannelManager, ChannelCollectionManager, RootUserManager, ProfileManager
from msghandle.models import MessageEventObjectFactory

from .token_ import discord_token
from .utils.cnflprvt import prioritized_bot_exists, initialize

__all__ = ["run_server", "_inst"]


class DiscordClient(Client):
    # Events: https://discordpy.readthedocs.io/en/latest/api.html#event-reference

    async def on_ready(self):
        from msghandle.botcmd.command import cmd_help

        DISCORD.logger.info(f"Logged in as {self.user}.")

        initialize(self.user.id)
        signal_discord_ready()

        await self.change_presence(activity=Activity(name=cmd_help.get_usage(), type=ActivityType.watching))

    async def on_message(self, message):
        # Prevent self reading and bot resonate
        if message.author == self.user or message.author.bot or prioritized_bot_exists(message.guild):
            return

        await handle_discord_main(
            MessageEventObjectFactory.from_discord(message)).to_platform(Platform.DISCORD).send_discord(message.channel)

    # noinspection PyMethodMayBeStatic
    async def on_private_channel_delete(self, channel: Union[DMChannel, GroupChannel]):
        if not ChannelManager.deregister(Platform.DISCORD, channel.id).is_success:
            warn_txt = f"Private Channel DELETED but the deregistration was failed. Channel token: {channel.id}"
            DISCORD.logger.warning(warn_txt)
            MailSender.send_email_async(warn_txt, subject="Discord private channel deletion failed")

    # noinspection PyMethodMayBeStatic
    async def on_private_channel_create(self, channel: Union[DMChannel, GroupChannel]):
        if not ChannelManager.register(Platform.DISCORD, channel.id, str(channel)).success:
            warn_txt = f"Private Channel CREATED but the registration was failed. Channel token: {channel.id}"
            DISCORD.logger.warning(warn_txt)
            MailSender.send_email_async(warn_txt, subject="Discord private channel creation failed")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    async def on_private_channel_update(self, before: GroupChannel, after: GroupChannel):
        if str(before) != str(after) \
                and not ChannelManager.update_channel_default_name(Platform.DISCORD, after.id, str(after)).is_success:
            warn_txt = f"Private Channel Name UPDATED but the name was not updated. Channel token: {after.id} / " \
                       f"Name: {str(before)} to {str(after)}"
            DISCORD.logger.warning(warn_txt)
            MailSender.send_email_async(warn_txt, subject="Discord private channel name update failed")

    # noinspection PyMethodMayBeStatic
    async def on_guild_channel_delete(self, channel: Union[TextChannel, VoiceChannel, CategoryChannel]):
        if channel.type == ChannelType.text \
                and not ChannelManager.deregister(Platform.DISCORD, channel.id).is_success:
            warn_txt = f"Guild Channel DELETED but the deregistration was failed. Channel token: {channel.id}"
            DISCORD.logger.warning(warn_txt)
            MailSender.send_email_async(warn_txt, subject="Discord guild channel deletion failed")

    # noinspection PyMethodMayBeStatic
    async def on_guild_channel_create(self, channel: Union[TextChannel, VoiceChannel, CategoryChannel]):
        if channel.type == ChannelType.text:
            reg_result = ChannelManager.register(Platform.DISCORD, channel.id, channel_full_repr(channel))

            if not reg_result.success:
                warn_txt = f"Guild Channel CREATED but the registration was failed. Channel token: {channel.id}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord guild channel creation failed")

            if not ChannelCollectionManager.register(
                    Platform.DISCORD, channel.guild.id, reg_result.model.id, str(channel.guild)).success:
                warn_txt = f"Guild Channel CREATED but the collection registration was failed. " \
                           f"Channel token: {channel.id}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord channel collection creation failed")

    # noinspection PyMethodMayBeStatic
    async def on_guild_channel_update(
            self,
            before: Union[TextChannel, VoiceChannel, CategoryChannel],
            after: Union[TextChannel, VoiceChannel, CategoryChannel]):
        if str(before) != str(after):
            update_result = ChannelCollectionManager.update_default_name(
                Platform.DISCORD, after.guild.id, channel_full_repr(after))

            if not update_result.is_success:
                warn_txt = f"Guild Channel Name UPDATED but the name was not updated. " \
                           f"Channel token: {after.id}"
                DISCORD.logger.warning(warn_txt)
                MailSender.send_email_async(warn_txt, subject="Discord guild channel name update failed")

    # noinspection PyMethodMayBeStatic
    async def on_member_join(self, member: Member):
        udata_result = RootUserManager.get_root_data_onplat(Platform.DISCORD, member.id, auto_register=True)
        cdata = ChannelManager.get_channel_token(Platform.DISCORD, member.guild.id, auto_register=True)

        if udata_result.success and cdata:
            ProfileManager.register_new_default_async(udata_result.model.id, cdata.id)

    # noinspection PyMethodMayBeStatic
    async def on_member_remove(self, member: Member):
        udata_result = RootUserManager.get_root_data_onplat(Platform.DISCORD, member.id, auto_register=True)
        cdata = ChannelManager.get_channel_token(Platform.DISCORD, member.guild.id, auto_register=True)

        if udata_result.success and cdata:
            ProfileManager.mark_unavailable_async(udata_result.model.id, cdata.id)

    async def on_guild_join(self, guild: Guild):
        pass

    async def on_guild_remove(self, guild: Guild):
        pass

    async def on_group_join(self, channel: GroupChannel, user: User):
        pass

    async def on_group_remove(self, channel: GroupChannel, user: User):
        pass


class DiscordClientWrapper:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._core = DiscordClient(loop=self._loop)

    def run(self, token):
        self._core.run(token)

    async def start(self, token):
        await self._core.start(token)

    @param_type_ensure
    def get_user_name_safe(self, uid: int) -> Optional[str]:
        udata = self._core.get_user(uid)

        if udata:
            return str(udata)
        else:
            return None

    @param_type_ensure
    def get_guild(self, gid: int) -> Optional[Guild]:
        return self._core.get_guild(gid)

    def latency(self) -> float:
        return self._core.latency

    @property
    def discord_client(self):
        return self._core

    @property
    def discord_loop(self):
        return self._loop


_inst = DiscordClientWrapper()


def run_server():
    # Obtained from https://github.com/Rapptz/discord.py/issues/710#issuecomment-395609297
    thread = threading.Thread(target=_inst.discord_loop.run_until_complete, args=(_inst.start(discord_token),))
    thread.start()
