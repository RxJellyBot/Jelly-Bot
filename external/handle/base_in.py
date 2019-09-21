from abc import ABC
from typing import Any

from bson import ObjectId
from linebot.models import TextMessage, MessageEvent
from discord import Message, ChannelType, TextChannel

from mongodb.factory import ChannelManager
from external.handle import logger
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
    def __init__(self, raw: Any, platform: Platform, text: Any, channel_oid: ObjectId = None):
        super().__init__(raw, platform, text)
        self.text = text
        self.channel_oid = channel_oid

    @staticmethod
    def convert(e: EventObject, t: str, channel_oid: ObjectId):
        return TextEventObject(e.raw, e.platform, t, channel_oid)

    @property
    def recorded_channel(self):
        return self.channel_oid is not None


class EventObjectFactory:
    DiscordAcceptedChannelTypes = (ChannelType.text, ChannelType.private, ChannelType.group)

    @staticmethod
    def from_line(event: MessageEvent) -> EventObject:
        channel_model = ChannelManager.get_channel_token(Platform.LINE, event.source.sender_id, auto_register=True)
        if isinstance(event.message, TextMessage):
            return TextEventObject(event, Platform.LINE, event.message.text, channel_model.id)
        else:
            logger.logger.warning(f"Unhandled LINE message event. {type(event.message)}")

    @staticmethod
    def from_discord(message: Message) -> EventObject:
        if message.channel.type not in EventObjectFactory.DiscordAcceptedChannelTypes:
            raise ValueError(
                f"Channel type not supported. ({message.channel.channel_type})"
                f"Currently supported channel types: {', '.join(EventObjectFactory.DiscordAcceptedChannelTypes)}")

        channel_model = ChannelManager.get_channel_token(Platform.DISCORD, message.channel.id, auto_register=True)
        return TextEventObject(message, Platform.DISCORD, message.content, channel_model.id)

    @staticmethod
    def from_direct(message: str):
        return TextEventObject(message, Platform.UNKNOWN, message)
