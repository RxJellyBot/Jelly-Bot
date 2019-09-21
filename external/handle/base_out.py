from abc import ABC

from flags import MessageType


class HandledEventObject(ABC):
    def __init__(self, msg_type: MessageType, content: str):
        self.content = content
        self.msg_type = msg_type


class HandledEventObjectText(HandledEventObject):
    def __init__(self, content: str):
        super().__init__(MessageType.TEXT, content)
