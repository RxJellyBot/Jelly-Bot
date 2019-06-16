from ._base import BaseField


class ModelField(BaseField):
    def __init__(self, key, model_cls, instance=None, allow_none=True):
        super().__init__(key, instance, allow_none)
        if model_cls is None:
            raise ValueError(f"`model_cls` needs to be specified for parsing.")
        else:
            self._model_cls = model_cls

    @property
    def model_cls(self):
        return self._model_cls

    @property
    def expected_types(self):
        from models import Model
        return Model

    def is_value_valid(self, value) -> bool:
        return self.is_type_matched(value)
