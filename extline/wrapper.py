import os
import sys
from typing import List, Union

from linebot import LineBotApi
from linebot.models import TextSendMessage

__all__ = ["line_api", "_inst", "LineApiUtils"]


line_token = os.environ.get("LINE_TOKEN")
if not line_token:
    print("Specify Line webhook access token as LINE_TOKEN in environment variables.")
    sys.exit(1)


line_api = LineBotApi(line_token)


class LineApiWrapper:
    def __init__(self):
        self._core = line_api

    def reply_text(self, reply_token, message: Union[str, List[str]]):
        if isinstance(message, str):
            send_messages = TextSendMessage(text=message)
        elif isinstance(message, list):
            send_messages = [TextSendMessage(text=msg) for msg in message]
        else:
            raise ValueError("Message should be either in `list` of `str` or `str`.")

        self._core.reply_message(reply_token, send_messages)


class LineApiUtils:
    @staticmethod
    def get_channel_id(event):
        return event.sender_id

    @staticmethod
    def get_user_id(event):
        return event.sender_id


_inst = LineApiWrapper()
