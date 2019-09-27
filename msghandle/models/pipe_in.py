from abc import ABC
from typing import Any, Optional, Union

from bson import ObjectId
from linebot.models import TextMessage, MessageEvent
from discord import Message, ChannelType

from models import ChannelModel, RootUserModel
from mongodb.factory import ChannelManager, RootUserManager
from extutils.emailutils import MailSender
from msghandle import logger
from flags import Platform


class EventObject(ABC):
    def __init__(self, raw: Any, platform: Platform):
        self.raw = raw
        self.platform = platform


class MessageEventObject(EventObject, ABC):
    def __init__(self, raw: Any, platform: Platform, content: Any):
        super().__init__(raw, platform)
        self.content = content


class TextEventObject(MessageEventObject):
    def __init__(self, raw: Any, platform: Platform, text: Any,
                 channel_oid: ObjectId = None, root_oid: ObjectId = None):
        super().__init__(raw, platform, text)
        self.text = text
        self.channel_oid = channel_oid
        self.root_oid = root_oid

    @staticmethod
    def convert(e: EventObject, t: str, channel_oid: ObjectId):
        return TextEventObject(e.raw, e.platform, t, channel_oid)

    @property
    def recorded_channel(self):
        return self.channel_oid is not None


class EventObjectFactory:
    DiscordAcceptedChannelTypes = (ChannelType.text, ChannelType.private, ChannelType.group)

    @staticmethod
    def _ensure_channel_(platform: Platform, token: Union[int, str]) -> Optional[ChannelModel]:
        ret = ChannelManager.get_channel_token(platform, token, auto_register=True)
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
    def from_line(event: MessageEvent) -> EventObject:
        from extline import LineApiUtils

        user_model = EventObjectFactory._ensure_user_idt_(Platform.LINE, LineApiUtils.get_user_id(event))
        channel_model = EventObjectFactory._ensure_channel_(Platform.LINE, LineApiUtils.get_channel_id(event))
        if isinstance(event.message, TextMessage):
            return TextEventObject(event, Platform.LINE, event.message.text, channel_model.id, user_model.id)
        else:
            logger.logger.warning(f"Unhandled LINE message event. {type(event.message)}")

    @staticmethod
    def from_discord(message: Message) -> EventObject:
        if message.channel.type not in EventObjectFactory.DiscordAcceptedChannelTypes:
            raise ValueError(
                f"Channel type not supported. ({message.channel.channel_type})"
                f"Currently supported channel types: {', '.join(EventObjectFactory.DiscordAcceptedChannelTypes)}")

        user_model = EventObjectFactory._ensure_user_idt_(Platform.DISCORD, message.author.id)
        channel_model = EventObjectFactory._ensure_channel_(Platform.DISCORD, message.channel.id)
        return TextEventObject(message, Platform.DISCORD, message.content, channel_model.id, user_model.id)

    @staticmethod
    def from_direct(message: str):
        return TextEventObject(message, Platform.UNKNOWN, message)
