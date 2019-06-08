from extutils.flags import FlagCodeEnum
from ._base import BaseField


class IntegerField(BaseField):
    def __init__(self, key, num: int = None, allow_none=False, readonly=False):
        super().__init__(key, num, allow_none, readonly=readonly)

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)

    @classmethod
    def none_obj(cls):
        return 0

    @property
    def expected_types(self):
        return int


class FlagField(IntegerField):
    FLAG_TYPE: FlagCodeEnum = None

    def __init__(self, key, value=None, allow_none=False):
        self._type = self.__class__.FLAG_TYPE
        if self._type is None:
            raise ValueError("Need to specify the FLAG_TYPE class var.")

        super().__init__(key, value, allow_none)

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
            return self._type(value)

        return self.is_type_matched(value)
