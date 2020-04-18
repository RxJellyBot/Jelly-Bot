from extutils.flags import FlagCodeEnum
from flags import APICommand, AutoReplyContentType, Execode, Platform, ExtraContentType, MessageType, BotFeature, \
    PermissionLevel

from .int import IntegerField
from .exceptions import FieldFlagNotFound


class FlagField(IntegerField):
    FLAG_TYPE: FlagCodeEnum = None

    def __init__(self, key, default=None, allow_none=False, auto_cast=True):
        self._type = self.__class__.FLAG_TYPE
        if self._type is None:
            raise ValueError("Need to specify the FLAG_TYPE class var.")

        if default is None:
            default = self._type.default()

        super().__init__(key, default, allow_none, auto_cast=auto_cast)

    @classmethod
    def none_obj(cls):
        return cls.FLAG_TYPE.default()

    @property
    def expected_types(self):
        return int, self._type

    @property
    def desired_type(self):
        return self._type

    def _check_value_valid_not_none_(self, value, *, skip_type_check=False, pass_on_castable=False):
        if isinstance(value, int) and value not in self._type:
            raise FieldFlagNotFound(self.key, value, self._type)


class APICommandField(FlagField):
    FLAG_TYPE = APICommand


class AutoReplyContentTypeField(FlagField):
    FLAG_TYPE = AutoReplyContentType


class PlatformField(FlagField):
    FLAG_TYPE = Platform


class ExecodeField(FlagField):
    FLAG_TYPE = Execode


class ExtraContentTypeField(FlagField):
    FLAG_TYPE = ExtraContentType


class MessageTypeField(FlagField):
    FLAG_TYPE = MessageType


class BotFeatureField(FlagField):
    FLAG_TYPE = BotFeature


class PermissionLevelField(FlagField):
    FLAG_TYPE = PermissionLevel
