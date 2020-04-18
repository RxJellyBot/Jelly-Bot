from ._base import BaseField


class ModelField(BaseField):
    # noinspection PyUnresolvedReferences
    def __init__(self, key, model_cls, default=None, allow_none=True, auto_cast=True):
        if model_cls is None:
            raise ValueError(f"`model_cls` needs to be specified for parsing.")
        else:
            self._model_cls = model_cls

        if default is None:
            default = model_cls.generate_default()

        super().__init__(key, default, allow_none, auto_cast=auto_cast)

    @property
    def model_cls(self):
        return self._model_cls

    @property
    def expected_types(self):
        return self.model_cls

    def cast_to_desired_type(self, value):
        return self.desired_type(**value, from_db=True)
