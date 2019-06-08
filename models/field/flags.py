from flags import APIAction, AutoReplyContentType, TokenAction, Platform, PermissionCategory
from .int import FlagField


class APIActionTypeField(FlagField):
    FLAG_TYPE = APIAction


class AutoReplyContentTypeField(FlagField):
    FLAG_TYPE = AutoReplyContentType


class PermissionLevelField(FlagField):
    FLAG_TYPE = PermissionCategory


class PlatformField(FlagField):
    FLAG_TYPE = Platform


class TokenActionField(FlagField):
    FLAG_TYPE = TokenAction
