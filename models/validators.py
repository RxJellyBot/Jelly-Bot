import urllib.request
from typing import Any

from extutils import LineStickerManager
from flags import AutoReplyContentType


class AutoReplyValidators:
    @staticmethod
    def is_valid_content(type_: AutoReplyContentType, content: Any) -> bool:
        if not isinstance(type_, AutoReplyContentType):
            type_ = AutoReplyContentType(type_)

        if type_ == AutoReplyContentType.IMAGE:
            return _BaseValidators.is_content_image(content)

        if type_ == AutoReplyContentType.LINE_STICKER:
            return _BaseValidators.is_content_sticker(content)

        return True


class _BaseValidators:
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
