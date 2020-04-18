from typing import Any


class ModelDefaultValueExtItem:
    def __init__(self, s):
        self._name = s

    def __repr__(self):
        return f"<Default: {self._name}>"


class ModelDefaultValueExt:
    Required = ModelDefaultValueExtItem("Required")
    Optional = ModelDefaultValueExtItem("Optional")

    @staticmethod
    def is_default_val_ext(val: Any):
        return val in (ModelDefaultValueExt.Required, ModelDefaultValueExt.Optional)
