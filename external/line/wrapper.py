import os
import sys

from linebot import LineBotApi
from linebot.models import TextSendMessage

__all__ = ["line_api", "_inst"]


line_token = os.environ.get("LINE_TOKEN")
if not line_token:
    print("Specify Line webhook access token as LINE_TOKEN in environment variables.")
    sys.exit(1)


line_api = LineBotApi(line_token)


class LineApiWrapper:
    def __init__(self):
        self._core = line_api

    def reply_text(self, reply_token, message):
        self._core.reply_message(
            reply_token,
            TextSendMessage(text=message))


_inst = LineApiWrapper()
