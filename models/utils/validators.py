"""Module of the implementations to validate the auto-reply module content."""
from typing import Any

import requests

from JellyBot.systemconfig import AutoReply
from extutils import safe_cast
from extutils.imgproc import ImageValidator
from extutils.linesticker import LineStickerUtils
from flags import AutoReplyContentType

__all__ = ("AutoReplyValidator",)


class AutoReplyValidator:
    # noinspection PyArgumentList
    @staticmethod
    def is_valid_content(type_: AutoReplyContentType, content: Any, *, online_check=True) -> bool:
        if not isinstance(type_, AutoReplyContentType):
            type_ = AutoReplyContentType(type_)

        if type_ == AutoReplyContentType.TEXT:
            return 0 < len(content.strip()) <= AutoReply.MaxContentLength

        if type_ == AutoReplyContentType.IMAGE:
            return _BaseValidator.is_content_image(content, online_check)

        if type_ == AutoReplyContentType.LINE_STICKER:
            return _BaseValidator.is_content_sticker(content, online_check)

        return True


class _BaseValidator:
    @staticmethod
    def _check_image_online(content: Any) -> bool:
        try:
            # Add headers to prevent discord CDN failure
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                              "AppleWebKit/537.11 (KHTML, like Gecko) "
                              "Chrome/23.0.1271.95 Safari/537.11"
            }

            response_headers = requests.head(content, headers=headers, allow_redirects=True).headers

            return response_headers["Content-Type"].split("/", 1)[0] == "image"
        except Exception:
            return False

    @staticmethod
    def _check_image_offline(content: Any) -> bool:
        try:
            # is URL and either HTTP or HTTPS?
            if not content.startswith("http"):
                return False

            # extension is either png, jpg or jpeg?
            if not ImageValidator.is_valid_image_extension(content):
                return False

            return True
        except Exception:
            return False

    @staticmethod
    def is_content_image(content: Any, online_check) -> bool:
        """
        Check if ``content`` is an image.

        :param content: content to be checked
        :param online_check: if to perform online check (actually check if the content exists)
        :return:
        """
        if online_check:
            return _BaseValidator._check_image_online(content)

        return _BaseValidator._check_image_offline(content)

    @staticmethod
    def is_content_sticker(content: Any, online_check) -> bool:
        if online_check:
            return LineStickerUtils.is_sticker_exists(content)
        else:
            return safe_cast(content, int) is not None
