import os
import sys
from typing import List, Union, Optional

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage, SendMessage, Profile, ImageMessage

from flags import ChannelType
from models import ChannelModel
from extutils.logger import SYSTEM

__all__ = ["line_api", "_inst", "LineApiUtils"]


line_token = os.environ.get("LINE_TOKEN")
if not line_token:
    SYSTEM.logger.critical("Specify Line webhook access token as LINE_TOKEN in environment variables.")
    sys.exit(1)


line_api = LineBotApi(line_token)


class LineApiWrapper:
    def __init__(self):
        self._core = line_api

    def reply_text(self, reply_token, message: Union[str, List[str]]):
        # Force cast messages to `str` because sometimes it may be __proxy__
        if isinstance(message, str):
            send_messages = TextSendMessage(text=str(message))
        elif isinstance(message, list):
            send_messages = [TextSendMessage(text=str(msg)) for msg in message]
        else:
            raise ValueError("Message should be either in `list` of `str` or `str`.")

        self._core.reply_message(reply_token, send_messages)

    def reply_message(self, reply_token, messages: Union[SendMessage, List[SendMessage]]):
        # Force cast messages to `str` because sometimes it may be __proxy__
        if isinstance(messages, TextSendMessage):
            messages = TextSendMessage(text=str(messages.text))
        elif isinstance(messages, list):
            messages = [TextSendMessage(text=str(msg.text)) if isinstance(msg, TextSendMessage) else msg
                        for msg in messages]
        else:
            raise ValueError("Message should be either in `list` of `TextSendMessage` or `TextSendMessage`.")

        self._core.reply_message(reply_token, messages)

    def get_profile(self, uid, channel_data: Optional[ChannelModel] = None) -> Optional[Profile]:
        ctype = ChannelType.UNKNOWN

        if channel_data:
            ctype = LineApiUtils.get_channel_type(channel_data.token)

        try:
            if ctype == ChannelType.GROUP_PUB_TEXT:
                return self._core.get_group_member_profile(channel_data.token, uid, timeout=1000)
            elif ctype == ChannelType.GROUP_PRV_TEXT:
                return self._core.get_room_member_profile(channel_data.token, uid, timeout=1000)
            else:
                return self._core.get_profile(uid, timeout=1000)
        except LineBotApiError as ex:
            if ex.status_code == 404:
                return None
            else:
                raise ex

    def get_user_name_safe(self, uid, channel_data: Optional[ChannelModel] = None) -> Optional[str]:
        prof = self.get_profile(uid, channel_data)

        if prof:
            return prof.display_name
        else:
            return None

    def get_image_base64(self, message: ImageMessage) -> str:
        return self._core.get_message_content(str(message.id)).content


class LineApiUtils:
    @staticmethod
    def get_channel_id(event):
        return event.source.sender_id

    @staticmethod
    def get_user_id(event, destination=None):
        ret = event.source.user_id
        if not ret:
            ret = destination

        return ret

    @staticmethod
    def get_channel_type(channel_token: str):
        key = channel_token[0]
        if key == "U":
            return ChannelType.PRIVATE_TEXT
        elif key == "C":
            return ChannelType.GROUP_PUB_TEXT
        elif key == "R":
            return ChannelType.GROUP_PRV_TEXT
        else:
            return ChannelType.UNKNOWN


_inst = LineApiWrapper()
