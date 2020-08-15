"""This module contains various wrappers of the required objects for the LINE bot webhook."""
import os
import sys
from typing import List, Union, Optional

import requests
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage, SendMessage, Profile, ImageMessage

from flags import ChannelType
from models import ChannelModel
from extutils.imgproc import ImageContentProcessor
from extutils.logger import SYSTEM

__all__ = ("LineApiUtils", "LineApiWrapper",)

line_token = os.environ.get("LINE_TOKEN")
if not line_token:
    SYSTEM.logger.critical("Specify Line webhook access token as LINE_TOKEN in environment variables.")
    sys.exit(1)

_line_api = LineBotApi(line_token)


class _LineApiWrapper:
    """LINE API wrapper class."""

    def __init__(self):
        self._core = _line_api

    def reply_text(self, reply_token, messages: Union[str, List[str]]):
        """
        Function to reply text message.

        :param reply_token: LINE message event reply token
        :param messages: messages to reply

        :raises ValueError: if the type of `messages` is unexpected/unhandled
        """
        # Force cast messages to `str` because sometimes it may be __proxy__
        if isinstance(messages, str):
            send_messages = TextSendMessage(text=str(messages))
        elif isinstance(messages, list):
            send_messages = [TextSendMessage(text=str(msg)) for msg in messages]
        else:
            raise ValueError("Message should be either in `list` of `str` or `str`.")

        self._core.reply_message(reply_token, send_messages)

    def reply_message(self, reply_token, messages: Union[SendMessage, List[SendMessage]]):
        """
        Function to reply message with the given packed message object.

        :param reply_token: LINE message event reply token
        :param messages: messages to reply
        :raises ValueError: if the type of `messages` is unexpected/unhandled
        """
        # Force cast messages to `str` because sometimes it may be __proxy__
        if isinstance(messages, TextSendMessage):
            messages = TextSendMessage(text=str(messages.text))
        elif isinstance(messages, list):
            messages = [TextSendMessage(text=str(msg.text)) if isinstance(msg, TextSendMessage) else msg
                        for msg in messages]
        else:
            raise ValueError("Message should be either in `List[SendMessage]` or `SendMessage`.")

        self._core.reply_message(reply_token, messages)

    def get_profile(self, uid: str, *, channel_model: Optional[ChannelModel] = None) -> Optional[Profile]:
        """
        Get the profile of the specified user.

        Info of a user who does not add the bot as a friend is generally ungettable.
        However, if the bot and the user are in a same group, the info will then be gettable.

        Because of this, providing `channel_model` whenever it's possible **IS RECOMMENDED**.

        :param uid: LINE UID of the user
        :param channel_model: `ChannelModel` to be used to get the info
        :return: LINE profile object if exists
        """
        ctype = ChannelType.UNKNOWN

        if channel_model:
            ctype = LineApiUtils.get_channel_type(channel_model.token)

        try:
            if ctype == ChannelType.GROUP_PUB_TEXT:
                return self._core.get_group_member_profile(channel_model.token, uid, timeout=1000)

            if ctype == ChannelType.GROUP_PRV_TEXT:
                return self._core.get_room_member_profile(channel_model.token, uid, timeout=1000)

            return self._core.get_profile(uid, timeout=1000)
        except LineBotApiError as ex:
            if ex.status_code == 404:
                return None

            raise ex
        except requests.exceptions.ConnectionError:
            return self.get_profile(uid, channel_model=channel_model)

    def get_user_name_safe(self, uid, *, channel_model: Optional[ChannelModel] = None) -> Optional[str]:
        """
        Safely get the user name of a user.

        Info of a user who does not add the bot as a friend is generally ungettable.
        However, if the bot and the user are in a same group, the info will then be gettable.

        Because of this, providing `channel_model` whenever it's possible **IS RECOMMENDED**.

        :param uid: LINE UID of the user
        :param channel_model: `ChannelModel` to be used to get the name
        :return: user name if found
        """
        prof = self.get_profile(uid, channel_model=channel_model)

        if prof:
            return prof.display_name

        return None

    def get_image_base64_str(self, message: ImageMessage) -> str:
        """
        Get the base64 string of the image in ``message``.

        :param message: the image message to get the content
        :return: a base64 string representing the image in `message`
        """
        return ImageContentProcessor.binary_img_to_base64_str(self._core.get_message_content(str(message.id)).content)


class LineApiUtils:
    """Various utils to control the data comes from LINE API."""

    @staticmethod
    def get_channel_id(event):
        """
        Get the source channel ID of `event`.

        This channel ID could be either a user (**U**), a room (**R**) or a group (**C**).

        :param event: event to get the source channel ID
        :return: source channel ID of the event
        """
        return event.source.sender_id

    @staticmethod
    def get_user_id(event, destination=None):
        """
        Get the source user ID of `event`.

        If not found, ``destination`` will be returned if provided.

        :param event: event to get the source user ID
        :param destination: destination of the event
        :return: source user ID of the event
        """
        ret = event.source.user_id
        if not ret:
            ret = destination

        return ret

    @staticmethod
    def get_channel_type(channel_token: str) -> ChannelType:
        """
        Get the channel type by parsing `channel_token`.

        :param channel_token: LINE channel token to be parsed
        :return: channel type according to `channel_token`
        """
        key = channel_token[0]

        if key == "U":
            return ChannelType.PRIVATE_TEXT

        if key == "C":
            return ChannelType.GROUP_PUB_TEXT

        if key == "R":
            return ChannelType.GROUP_PRV_TEXT

        return ChannelType.UNKNOWN


LineApiWrapper = _LineApiWrapper()
