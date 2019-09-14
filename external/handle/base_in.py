from abc import ABC
from dataclasses import dataclass, field
from typing import Any

from linebot.models import TextMessage

from external.handle import logger
from flags import Platform


@dataclass
class EventObject(ABC):
    raw: Any
    platform: Platform


@dataclass
class MessageEventObject(EventObject, ABC):
    content: Any


@dataclass
class TextEventObject(MessageEventObject):
    text: str
    content: str = field(init=False)

    def __post_init__(self):
        self.content = self.text

    @staticmethod
    def convert(e: EventObject, t: str):
        return TextEventObject(text=t, raw=e.raw, platform=e.platform)


class EventObjectFactory:
    @staticmethod
    def from_line(event) -> EventObject:
        if isinstance(event.message, TextMessage):
            return TextEventObject(text=event.message.text, platform=Platform.LINE, raw=event)
        else:
            logger.logger.warning(f"Unhandled LINE message event. {type(event.message)}")

    @staticmethod
    def from_discord(message) -> EventObject:
        return TextEventObject(text=message.content, platform=Platform.DISCORD, raw=message)
