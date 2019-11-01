from abc import ABC
from typing import Any, Optional, Union

from bson import ObjectId
from linebot.models import TextMessage, MessageEvent
from discord import Message, ChannelType

from models import ChannelModel, RootUserModel
from mongodb.factory import ChannelManager, RootUserManager
from extutils.emailutils import MailSender
from msghandle import logger
from flags import Platform, MessageType, ChannelType as SysChannelType


class Event(ABC):
    def __init__(
            self, raw: Any, channel_model: ChannelModel = None, sys_ctype: SysChannelType = None):
        if not sys_ctype:
            sys_ctype = SysChannelType.identify(channel_model.platform, channel_model.token)

        self.raw = raw
        self.channel_model = channel_model
        self.channel_type = sys_ctype

    @property
    def platform(self) -> Platform:
        return self.channel_model.platform

    @property
    def user_token(self) -> Optional:
        if self.platform == Platform.LINE:
            from extline import LineApiUtils

            return LineApiUtils.get_user_id(self.raw)
        elif self.platform == Platform.DISCORD:
            return self.raw.author.id
        else:
            return None


class MessageEventObject(Event, ABC):
    def __init__(
            self, raw: Any, content: Any, channel_model: ChannelModel = None, user_model: RootUserModel = None,
            sys_ctype: SysChannelType = None):
        super().__init__(raw, channel_model, sys_ctype)
        self.content = content
        self.user_model = user_model

    @property
    def message_type(self) -> MessageType:
        raise NotImplementedError()

    @property
    def channel_oid(self) -> ObjectId:
        return self.channel_model.id

    @property
    def root_oid(self) -> ObjectId:
        return self.user_model.id


class TextMessageEventObject(MessageEventObject):
    def __init__(
            self, raw: Any, text: Any, channel_model: ChannelModel = None, user_model: RootUserModel = None,
            sys_ctype: SysChannelType = None):
        super().__init__(raw, text, channel_model, user_model, sys_ctype)
        self.text = text

    @property
    def message_type(self) -> MessageType:
        return MessageType.TEXT


class MessageEventObjectFactory:
    DiscordAcceptedChannelTypes = (ChannelType.text, ChannelType.private, ChannelType.group)

    @staticmethod
    def _ensure_channel_(platform: Platform, token: Union[int, str], default_name: str = None) -> Optional[ChannelModel]:
        ret = ChannelManager.get_channel_token(platform, token, auto_register=True, default_name=default_name)
        if not ret:
            MailSender.send_email_async(f"Platform: {platform} / Token: {token}", subject="Channel Registration Failed")

        return ret

    @staticmethod
    def _ensure_user_idt_(platform: Platform, token: Union[int, str], traceback=None) -> Optional[RootUserModel]:
        result = RootUserManager.register_onplat(platform, token)
        if not result.success:
            MailSender.send_email_async(
                f"Platform: {platform} / Token: {token}<hr>"
                f"Outcome: {result.outcome}<hr>"
                f"Conn Outcome: {result.conn_outcome}<hr>"
                f"Identity Registration Result: {result.idt_reg_result.serialize()}<hr>"
                f"Exception: {traceback.format_exception(None, result.exception, result.exception.__traceback__)}",
                subject="User Registration Failed")

        return result.model

    @staticmethod
    def from_line(event: MessageEvent) -> MessageEventObject:
        from extline import LineApiUtils

        user_model = MessageEventObjectFactory._ensure_user_idt_(Platform.LINE, LineApiUtils.get_user_id(event))
        channel_model = MessageEventObjectFactory._ensure_channel_(
            Platform.LINE, LineApiUtils.get_channel_id(event))
        if isinstance(event.message, TextMessage):
            return TextMessageEventObject(event, event.message.text, channel_model, user_model)
        else:
            logger.logger.warning(f"Unhandled LINE message event. {type(event.message)}")

    @staticmethod
    def from_discord(message: Message) -> MessageEventObject:
        from extdiscord.utils import channel_repr

        if message.channel.type not in MessageEventObjectFactory.DiscordAcceptedChannelTypes:
            raise ValueError(
                f"Channel type not supported. ({message.channel.type})"
                f"Currently supported channel types: "
                f"{', '.join(MessageEventObjectFactory.DiscordAcceptedChannelTypes)}")

        user_model = MessageEventObjectFactory._ensure_user_idt_(Platform.DISCORD, message.author.id)
        channel_model = MessageEventObjectFactory._ensure_channel_(
            Platform.DISCORD, message.channel.id, channel_repr(message))
        return TextMessageEventObject(
            message, message.content, channel_model, user_model,
            SysChannelType.trans_from_discord(message.channel.type))
