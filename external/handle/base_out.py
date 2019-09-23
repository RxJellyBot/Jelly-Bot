from abc import ABC
from collections import Callable
from typing import Iterator, List, Any

from flags import MessageType


class HandledEventObject(ABC):
    def __init__(self, msg_type: MessageType, content: str):
        self.content = content
        self.msg_type = msg_type

    def to_json(self):
        return {"content": str(self.content), "type": self.msg_type}


class HandledEventObjectText(HandledEventObject):
    def __init__(self, content: str):
        super().__init__(MessageType.TEXT, content)


class HandledEventsHolder:
    def __init__(self, init_items: List[HandledEventObject] = None):
        if not init_items:
            init_items = []

        self._core = init_items

    def __iter__(self):
        for item in self._core:
            yield item

    def get_contents_condition(self, lambda_fn: Callable) -> Iterator:
        return filter(lambda_fn, self._core)

    def to_json(self):
        return [item.to_json() for item in self._core]
