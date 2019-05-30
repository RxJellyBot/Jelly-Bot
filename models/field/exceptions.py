from typing import Union, Tuple


class FieldReadOnly(Exception):
    def __init__(self, field_name):
        super().__init__(f"This field ({field_name}) is readonly.")


class FieldTypeMismatch(Exception):
    def __init__(self, got: type, expected: Union[type, Tuple[type]] = None, field_name: str = None):
        self._got_type = got
        self._expected_types = expected
        self._field_name = field_name

        if expected is None:
            self._expected_name = "(Unknown)"
        elif isinstance(expected, type):
            self._expected_name = expected.__name__
        else:
            self._expected_name = " or ".join([t.__name__ for t in expected])

        super().__init__(f"Field type mismatch. "
                         f"Expected: {self._expected_name}, Got: {got.__name__}")

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def got_type(self) -> type:
        return self._got_type

    @property
    def expected_types(self) -> Union[type, Tuple[type]]:
        return self._expected_types


class FieldValueInvalid(Exception):
    def __init__(self, value):
        self._value = value
        super().__init__(f"Invalid Field Value: {value}")

    @property
    def value(self) -> type:
        return self._value


class MaxLengthReachedError(Exception):
    def __init__(self, max_len: int):
        super().__init__(f"Max length ({max_len}) reached.")
