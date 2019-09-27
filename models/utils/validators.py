import urllib.request
from typing import Any

from JellyBot.systemconfig import AutoReply

from extutils.line_sticker import LineStickerManager
import flags


class AutoReplyValidators:
    # noinspection PyArgumentList
    @staticmethod
    def is_valid_content(type_: flags.AutoReplyContentType, content: Any) -> bool:
        if not isinstance(type_, flags.AutoReplyContentType):
            type_ = flags.AutoReplyContentType(type_)

        if type_ == flags.AutoReplyContentType.IMAGE:
            return _BaseValidators.is_content_image(content)

        if type_ == flags.AutoReplyContentType.LINE_STICKER:
            return _BaseValidators.is_content_sticker(content)

        if type_ == flags.AutoReplyContentType.TEXT:
            return len(content) <= AutoReply.MaxContentLength

        return True


class _BaseValidators:
    # noinspection PyBroadException
    @staticmethod
    def is_content_image(content: Any) -> bool:
        try:
            with urllib.request.urlopen(content) as response:
                if response.info().get_content_maintype() != "image":
                    return False
                else:
                    return True
        except Exception:
            return False

    @staticmethod
    def is_content_sticker(content: Any) -> bool:
        return LineStickerManager.is_sticker_exists(content)
