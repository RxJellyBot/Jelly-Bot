from abc import ABC

from rxtoolbox.flags import FlagCodeEnum
from flags import (
    APICommand, AutoReplyContentType, Execode, Platform, ExtraContentType,
    MessageType, BotFeature, PermissionLevel
)

from .int import IntegerField
from .exceptions import FieldFlagNotFoundError, FieldFlagDefaultUndefinedError, FieldValueInvalidError, \
    FieldCastingFailedError


class FlagField(IntegerField, ABC):
    """
    Base class of the ``Flag`` field.

    To use, create a new class using this class as the base class
    and specify the class variable ``FLAG_TYPE``.
    """
    FLAG_TYPE: FlagCodeEnum = None

    def __init__(self, key, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``
        - ``default`` - Default value of :class:`FlagCodeEnum`

        :raises ValueError: if class variable ``FLAG_TYPE`` not set
        :raises FieldFlagDefaultUndefined: if the default value of ``FLAG_TYPE`` not defined

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        self._type = self.__class__.FLAG_TYPE
        if self._type is None:
            raise ValueError("Need to specify the FLAG_TYPE class var.")

        try:
            if "default" not in kwargs:
                kwargs["default"] = self._type.default()
        except ValueError:
            raise FieldFlagDefaultUndefinedError(key, self._type)

        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        super().__init__(key, **kwargs)

    def none_obj(self):
        return self.FLAG_TYPE.default()

    @property
    def expected_types(self):
        return self._type, int, str

    def _check_value_valid_not_none(self, value):
        try:
            self._type.cast(value)
        except TypeError:
            raise FieldValueInvalidError(self.key, value)
        except ValueError:
            raise FieldFlagNotFoundError(self.key, value, self._type)

    def _cast_to_desired_type(self, value):
        try:
            return self._type.cast(value)
        except (TypeError, ValueError) as e:
            raise FieldCastingFailedError(self.key, value, self.desired_type, exc=e)


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
