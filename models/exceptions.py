from abc import ABC
from typing import List, Type


class ModelConstructionError(Exception, ABC):
    pass


class InvalidModelError(ModelConstructionError):
    def __init__(self, model_name, reason):
        super().__init__(f"Invalid model `{model_name}`. Reason: {reason.code}")


class RequiredKeyUnfilledError(ModelConstructionError):
    def __init__(self, model_cls: Type, ks: List[str]):
        super().__init__(f"Required fields unfilled. Keys: {', '.join(ks)} / Model Class: {model_cls}")


class IdUnsupportedError(ModelConstructionError):
    def __init__(self, model_name):
        super().__init__(
            f"`{model_name}` is not designated to have `_id` field. Set `WITH_OID` to True to support this.")


class FieldKeyNotExistedError(AttributeError):
    def __init__(self, fk, model_name):
        super().__init__(f"Field key `{fk}` not existed in the model `{model_name}`.")


class JsonKeyNotExistedError(AttributeError):
    def __init__(self, fk, model_name):
        super().__init__(f"Json key `{fk}` not existed in the model `{model_name}`.")
