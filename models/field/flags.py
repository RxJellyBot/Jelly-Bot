from abc import ABC

from extutils.flags import FlagCodeEnum
from flags import APICommand, AutoReplyContentType, Execode, Platform, ExtraContentType, MessageType, BotFeature, \
    PermissionLevel

from .int import IntegerField
from .exceptions import FieldFlagNotFound


class FlagField(IntegerField, ABC):
    FLAG_TYPE: FlagCodeEnum = None

    def __init__(self, key, **kwargs):
        self._type = self.__class__.FLAG_TYPE
        if self._type is None:
            raise ValueError("Need to specify the FLAG_TYPE class var.")

        if "default" not in kwargs:
            kwargs["default"] = self._type.default()
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        super().__init__(key, **kwargs)

    @classmethod
    def none_obj(cls):
        return cls.FLAG_TYPE.default()

    @property
    def expected_types(self):
        return self._type

    @property
    def desired_type(self):
        return self._type

    def _check_value_valid_not_none_(self, value, *, skip_type_check=False, pass_on_castable=False):
        if isinstance(value, int) and self._type.cast(value) not in self._type:
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
