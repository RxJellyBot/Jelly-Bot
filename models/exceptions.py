from abc import ABC
from typing import List, Type

from flags import ModelValidityCheckResult


class ModelConstructionError(Exception, ABC):
    pass


class ModelOperationError(Exception, ABC):
    pass


class ModelKeyNotExistError(AttributeError, ABC):
    pass


class InvalidModelError(ModelConstructionError):
    """Raised if the model is invalid."""

    def __init__(self, model_name: str, reason: ModelValidityCheckResult):
        self._reason = reason
        super().__init__(f"Invalid model `{model_name}`. Reason: {repr(reason)}")

    @property
    def reason(self) -> ModelValidityCheckResult:
        """
        Get the invalid reason.

        :return: invalid reason
        """
        return self._reason


class InvalidModelFieldError(ModelConstructionError):
    def __init__(self, model_name: str, exception: Exception):
        self._inner = exception
        super().__init__(f"Invalid model `{model_name}`. Exception: {exception}")

    @property
    def inner_exception(self) -> Exception:
        return self._inner


class ModelUncastableError(ModelConstructionError):
    def __init__(self, model_name: str, reason: str):
        super().__init__(f"Model `{model_name}` cannot be casted. {reason}")


class RequiredKeyNotFilledError(ModelConstructionError):
    def __init__(self, model_cls: Type, ks: List[str]):
        super().__init__(f"Required fields not filled. Keys: {', '.join(ks)} / Model Class: {model_cls}")


class IdUnsupportedError(ModelConstructionError, KeyError, AttributeError):
    def __init__(self, model_name: str):
        super().__init__(
            f"`{model_name}` is not designated to have `_id` field. Set `WITH_OID` to True to support this.")


class FieldKeyNotExistError(ModelKeyNotExistError):
    def __init__(self, fk: str, model_name: str):
        super().__init__(f"Field key `{fk}` not existed in the model `{model_name}`.")


class JsonKeyNotExistedError(ModelKeyNotExistError):
    def __init__(self, fk: str, model_name: str):
        super().__init__(f"Json key `{fk}` not existed in the model `{model_name}`.")


class JsonKeyDuplicatedError(ModelConstructionError):
    def __init__(self, dup_key: str, model_name: str):
        super().__init__(f"Model `{model_name}` contains duplicated json key: {dup_key}.")


class DeleteNotAllowedError(ModelOperationError):
    def __init__(self, model_name: str):
        super().__init__(f"Not allowed to perform `del` on {model_name}")
