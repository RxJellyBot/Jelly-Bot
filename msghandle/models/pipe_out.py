from abc import ABC
from typing import List

from flags import MessageType, Platform
from JellyBot.systemconfig import LineApi, Discord


class HandledMessageEvent(ABC):
    def __init__(self, msg_type: MessageType, content: str):
        self.content = content
        self.msg_type = msg_type

    def to_json(self):
        return {"content": str(self.content), "type": self.msg_type}


class HandledMessageEventText(HandledMessageEvent):
    def __init__(self, content: str, bypass_multiline_check: bool = False):
        super().__init__(MessageType.TEXT, content)
        self.bypass_multiline_check = bypass_multiline_check


class HandledMessageCalculateResult(HandledMessageEventText):
    def __init__(self, content: str, latex: str):
        super().__init__(content)
        self.latex = latex

    @property
    def latex_available(self) -> bool:
        return self.latex != self.content

    @property
    def latex_for_html(self):
        return f"$${self.latex}$$"

    def to_json(self):
        return super().to_json().update({"latex": self.latex})


class HandledMessageEventsHolder:
    def __init__(self, init_items: List[HandledMessageEvent] = None):
        if not init_items:
            init_items = []

        self._core = init_items

    def __iter__(self):
        for item in self._core:
            yield item

    def to_json(self):
        return [item.to_json() for item in self._core]

    def to_platform(self, platform: Platform):
        from .out_plat import HandledEventsHolderPlatform

        if platform == Platform.LINE:
            return HandledEventsHolderPlatform(self, LineApi)
        if platform == Platform.DISCORD:
            return HandledEventsHolderPlatform(self, Discord)
