from abc import ABC
from typing import Union, Tuple, Any, Iterable


class FieldException(ABC, Exception):
    def __init__(self, key: str, *, error_msg: str = None):
        super().__init__(f"Field (Key: {key}) - {error_msg}")


class FieldReadOnly(FieldException):
    def __init__(self, key: str):
        super().__init__(key, error_msg="Readonly.")


class FieldTypeMismatch(FieldException):
    def __init__(self, key: str, actual: type, expected: Union[type, Iterable[type]] = None, *,
                 extra_message: str = None):
        if expected is None:
            expected_name = "(Unknown)"
        elif isinstance(expected, type):
            expected_name = expected.__name__
        else:
            expected_name = " or ".join([t.__name__ for t in expected])

        super().__init__(
            key,
            error_msg=f"Type mismatch. {extra_message or ''} "
                      f"Expected: {expected_name}, Actual: {actual.__name__}")


class FieldValueTypeMismatch(FieldException):
    def __init__(self, key: str, actual: type, expected: Union[type, Tuple[type]] = None, *,
                 extra_message: str = None):
        if expected is None:
            expected_name = "(Unknown)"
        elif isinstance(expected, type):
            expected_name = expected.__name__
        else:
            expected_name = " or ".join([t.__name__ for t in expected])

        super().__init__(
            key,
            error_msg=f"Type mismatch. {extra_message or ''} "
                      f"Expected: {expected_name}, Actual: {actual.__name__}")


class FieldValueInvalid(FieldException):
    def __init__(self, key: str, value: Any):
        super().__init__(key, error_msg=f"Invalid value: {value}")


class FieldCastingFailed(FieldException):
    def __init__(self, key: str, value: str, desired_type: type, *, exc: Exception = None):
        super().__init__(
            key,
            error_msg=f"Auto casting failed. Value: ({value}) {type(value)} / Desired type: {desired_type} / "
                      f"Exception: {exc}")


class FieldNoneNotAllowed(FieldException):
    def __init__(self, key: str):
        super().__init__(key, error_msg="`None` not allowed.")


class FieldEmptyValueNotAllowed(FieldException):
    def __init__(self, key: str):
        super().__init__(key, error_msg="Empty value not allowed.")


class FieldMaxLengthReached(FieldException):
    def __init__(self, key: str, cur_len: int, max_len: int):
        super().__init__(key, error_msg=f"Max length reached. {cur_len}/{max_len}")


class FieldInvalidUrl(FieldException):
    def __init__(self, key: str, url: str):
        super().__init__(key, error_msg=f"Invalid URL: {url}")


class FieldFlagNotFound(FieldException):
    def __init__(self, key: str, obj: Any, flag):
        super().__init__(key, error_msg=f"Object ({obj}) not found in the flag ({flag}).")


class FieldFlagDefaultUndefined(FieldException):
    def __init__(self, key: str, flag):
        super().__init__(key, error_msg=f"Default value of the flag ({flag}) undefined.")


class FieldRegexNotMatch(FieldException):
    def __init__(self, key: str, value: str, regex: str):
        super().__init__(key, error_msg=f"Regex ({regex}) not match with ({value}).")


class FieldInstanceClassInvalid(FieldException):
    def __init__(self, key: str, inst_cls):
        super().__init__(key, error_msg=f"Invalid field instance class type: {inst_cls}")


class FieldModelClassInvalid(FieldException):
    def __init__(self, key: str, model_cls):
        super().__init__(key, error_msg=f"Invalid model class type: {model_cls}")


class FieldValueNegative(FieldException):
    def __init__(self, key: str, val: Union[int, float]):
        super().__init__(key, error_msg=f"Field value should not be negative. (Actual: {val})")


class FieldInvalidDefaultValue(FieldException):
    def __init__(self, key: str, default_value: Any, *, exc: Exception = None):
        super().__init__(key, error_msg=f"Invalid default value. {default_value} - <{exc}>")
