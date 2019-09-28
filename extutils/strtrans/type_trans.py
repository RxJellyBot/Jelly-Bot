from datetime import datetime
from typing import Iterable

from bson import ObjectId
from django.utils.translation import gettext_lazy as _

from flags import AutoReplyContentType, PermissionCategory, Platform


def type_translation(type_: type):
    if isinstance(type_, str):
        return _("String")
    elif isinstance(type_, bool):
        return _("Boolean")
    elif isinstance(type_, int):
        return _("Integer")
    elif isinstance(type_, AutoReplyContentType):
        return _("Auto Reply Content Type")
    elif isinstance(type_, PermissionCategory):
        return _("Permission Category")
    elif isinstance(type_, Platform):
        return _("Platform")
    elif isinstance(type_, datetime):
        return _("Datetime")
    elif isinstance(type_, ObjectId):
        return _("ObjectId")
    elif isinstance(type_, Iterable):
        return _("Iterable (e.g. List, Array, Dictionary...)")
    elif isinstance(type_, type(None)):
        return _("(Null)")
    else:
        return type_.__qualname__
