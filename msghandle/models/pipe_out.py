from abc import ABC
from typing import List

from django.utils.translation import gettext_lazy as _
from sympy import latex, Rational

from extutils import safe_cast
from extutils.emailutils import MailSender
from flags import MessageType, Platform, AutoReplyContentType
from JellyBot.systemconfig import LineApi, Discord
from models.utils import AutoReplyValidators
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
        valid = \
            AutoReplyValidators.is_valid_content(response_model.content_type, response_model.content, online_check=True)

        if not valid:
            MailSender.send_email_async(f"Invalid auto-reply content detected.\n\n"
                                        f"Content: {response_model.content}\n"
                                        f"Content Type: {response_model.content_type.key}",
                                        subject="Invalid auto-reply content detected")
            return None

        if response_model.content_type == AutoReplyContentType.TEXT:
            return HandledMessageEventText(content=response_model.content, bypass_multiline_check=bypass_ml_check)
        elif response_model.content_type == AutoReplyContentType.IMAGE:
            return HandledMessageEventImage(image_url=response_model.content)
        elif response_model.content_type == AutoReplyContentType.LINE_STICKER:
            return HandledMessageEventLineSticker(sticker_id=response_model.content)
        else:
            return None


class HandledMessageEventText(HandledMessageEvent):
    def __init__(self, content: str, bypass_multiline_check: bool = False, force_extra: bool = False):
        """
        `bypass_multiline_check` | `force_extra` | Resulting action
        F | F | Checking multiline, if over length then extra, else normal
        F | T | Content will be stored as extra
        T | F | Content will be stored as normal
        T | T | Content will be stored as extra
        """
        super().__init__(MessageType.TEXT, content)
        self.force_extra = force_extra
        self.bypass_multiline_check = bypass_multiline_check


class HandledMessageEventImage(HandledMessageEvent):
    def __init__(self, image_url):
        super().__init__(MessageType.IMAGE, image_url)


class HandledMessageEventLineSticker(HandledMessageEvent):
    def __init__(self, sticker_id):
        super().__init__(MessageType.LINE_STICKER, sticker_id)


class HandledMessageCalculateResult(HandledMessageEventText):
    def __init__(self, expr_before: str, expr_after=None):
        content = str(_("**AUTO CALCULATOR**\n"
                        "Expression: `{}`\n"
                        "Result: `{}`").format(expr_before, expr_after))

        if not expr_after:
            expr_after = expr_before

        if isinstance(expr_after, Rational):
            content += "\n" + str(_("Evaluated: `{}`").format(float(expr_after)))

        super().__init__(content)
        self.latex = latex(expr_after)
        self.calc_result = str(expr_after)
        self.calc_expr = expr_before

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
    def __init__(self, channel_model, init_items: List[HandledMessageEvent] = None):
        if not init_items:
            init_items = []

        self._core = init_items
        self._channel_model = channel_model

    def __iter__(self):
        for item in self._core:
            yield item

    @property
    def has_item(self) -> bool:
        return len(self._core) > 0

    @property
    def channel_model(self):
        return self._channel_model

    def to_json(self):
        return [item.to_json() for item in self._core]

    def to_platform(self, platform: Platform):
        from .out_plat import HandledEventsHolderPlatform

        if platform == Platform.LINE:
            return HandledEventsHolderPlatform(self, LineApi)
        if platform == Platform.DISCORD:
            return HandledEventsHolderPlatform(self, Discord)
