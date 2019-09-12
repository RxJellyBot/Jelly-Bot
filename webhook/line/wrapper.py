from linebot.models import TextSendMessage

from .base import line_api


class LineApiWrapper:
    def __init__(self):
        self._core = line_api

    def reply_text(self, reply_token, message):
        self._core.reply_message(
            reply_token,
            TextSendMessage(text=message))


_inst = LineApiWrapper()
