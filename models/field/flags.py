from extutils.flags import FlagCodeEnum
from flags import APIAction, AutoReplyContentType, TokenAction, Platform
from .int import IntegerField


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

    # noinspection PyCallingNonCallable
    def is_value_valid(self, value) -> bool:
        if isinstance(value, int):
            return value in self._type

        return self.is_type_matched(value)


class APIActionTypeField(FlagField):
    FLAG_TYPE = APIAction


class AutoReplyContentTypeField(FlagField):
    FLAG_TYPE = AutoReplyContentType


class PlatformField(FlagField):
    FLAG_TYPE = Platform


class TokenActionField(FlagField):
    FLAG_TYPE = TokenAction
