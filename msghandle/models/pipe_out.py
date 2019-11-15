from abc import ABC
from typing import List
from gettext import gettext as _

from extutils import safe_cast
from flags import MessageType, Platform, AutoReplyContentType
from JellyBot.systemconfig import LineApi, Discord
from models import AutoReplyContentModel


class HandledMessageEvent(ABC):
    def __init__(self, msg_type: MessageType, content: str):
        self.content = content
        self.msg_type = msg_type

    def to_json(self):
        return {"content": str(self.content), "type": self.msg_type}

    @staticmethod
    def auto_reply_model_to_handled(response_model: AutoReplyContentModel, bypass_ml_check: bool):
        """
        Attempt to cast `AutoReplyContentModel` to be any the corresponding `HandledMessageEvent`.

        :return: Casted `HandledMessageEvent`. Return `None` if no corresponding `HandledMessageEvent`.
        """
        if response_model.content_type == AutoReplyContentType.TEXT:
            return HandledMessageEventText(content=response_model.content, bypass_multiline_check=bypass_ml_check)
        elif response_model.content_type == AutoReplyContentType.IMAGE:
            return HandledMessageEventImage(image_url=response_model.content)
        elif response_model.content_type == AutoReplyContentType.LINE_STICKER:
            return HandledMessageEventLineSticker(sticker_id=response_model.content)
        else:
            return None


class HandledMessageEventText(HandledMessageEvent):
    def __init__(self, content: str, bypass_multiline_check: bool = False):
        super().__init__(MessageType.TEXT, content)
        self.bypass_multiline_check = bypass_multiline_check


class HandledMessageEventImage(HandledMessageEvent):
    def __init__(self, image_url):
        super().__init__(MessageType.IMAGE, image_url)


class HandledMessageEventLineSticker(HandledMessageEvent):
    def __init__(self, sticker_id):
        super().__init__(MessageType.LINE_STICKER, sticker_id)


class HandledMessageCalculateResult(HandledMessageEventText):
    def __init__(self, calc_result: str, latex: str, calc_expr: str):
        super().__init__(_("**AUTO CALCULATOR**\n"
                           "Expression: {}\n"
                           "Result: {}").format(calc_expr, calc_result))
        self.latex = latex
        self.calc_result = calc_result
        self.calc_expr = calc_expr

    @property
    def latex_available(self) -> bool:
        if self.latex == self.calc_result:
            return False

        ltx = safe_cast(self.latex, float)
        crslt = safe_cast(self.calc_result, float)

        if ltx and crslt:
            return ltx != crslt
        else:
            return True

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
