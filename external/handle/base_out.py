from abc import ABC
from dataclasses import dataclass, field

from flags import MessageType


@dataclass
class HandledEventObject(ABC):
    msg_type: MessageType
    content: str


@dataclass
class HandledEventObjectText(HandledEventObject):
    msg_type: MessageType = field(init=False)

    def __post_init__(self):
        self.msg_type = MessageType.TEXT
