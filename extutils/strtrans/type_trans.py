"""Translate :class:`type` to :class:`str`."""
from datetime import datetime
from typing import Iterable

from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from flags import AutoReplyContentType, ProfilePermission, Platform


def type_translation(type_: type):  # noqa: C901
    """
    Get the description of type ``type_``.

    :param type_: type to get the description
    :return: description of `type_`
    """
    # pylint: disable=too-many-return-statements

    if issubclass(type_, str):
        return _("String")

    if issubclass(type_, bool):
        return _("Boolean")

    if issubclass(type_, int):
        return _("Integer")

    if issubclass(type_, AutoReplyContentType):
        return _("Auto Reply Content Type")

    if issubclass(type_, ProfilePermission):
        return _("Permission Category")

    if issubclass(type_, Platform):
        return _("Platform")

    if issubclass(type_, datetime):
        return _("Datetime")

    if issubclass(type_, ObjectId):
        return _("ObjectId")

    if issubclass(type_, Iterable):
        return _("Iterable (e.g. List, Array, Dictionary...)")

    if issubclass(type_, type(None)):
        return _("(Null)")

    return type_.__qualname__
