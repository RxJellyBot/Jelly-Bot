from datetime import datetime
from typing import Iterable

from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from flags import AutoReplyContentType, ProfilePermission, Platform


def type_translation(type_: type):  # noqa: C901
    if issubclass(type_, str):
        return _("String")
    elif issubclass(type_, bool):
        return _("Boolean")
    elif issubclass(type_, int):
        return _("Integer")
    elif issubclass(type_, AutoReplyContentType):
        return _("Auto Reply Content Type")
    elif issubclass(type_, ProfilePermission):
        return _("Permission Category")
    elif issubclass(type_, Platform):
        return _("Platform")
    elif issubclass(type_, datetime):
        return _("Datetime")
    elif issubclass(type_, ObjectId):
        return _("ObjectId")
    elif issubclass(type_, Iterable):
        return _("Iterable (e.g. List, Array, Dictionary...)")
    elif issubclass(type_, type(None)):
        return _("(Null)")
    else:
        return type_.__qualname__
