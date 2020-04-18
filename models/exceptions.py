from abc import ABC


class ModelConstructionError(Exception, ABC):
    pass


class InvalidModelError(ModelConstructionError):
    def __init__(self, model_name, reason):
        super().__init__(f"Invalid model `{model_name}`. Reason: {reason.code}")


class RequiredKeyUnfilledError(ModelConstructionError):
    def __init__(self, ks):
        super().__init__(f"Required fields unfilled. ({', '.join(ks)})")


class IdUnsupportedError(ModelConstructionError):
    def __init__(self, model_name):
        super().__init__(
            f"`{model_name}` is not designated to have `_id` field. Set `with_oid` to True to support this.")


class KeyNotExistedError(ModelConstructionError):
    def __init__(self, fk, model_name):
        super().__init__(f"Field key `{fk}` not existed in the model `{model_name}`.")
