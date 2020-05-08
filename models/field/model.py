from ._base import BaseField


class ModelField(BaseField):
    # noinspection PyUnresolvedReferences
    def __init__(self, key, model_cls, **kwargs):
        if model_cls is None:
            raise ValueError("`model_cls` needs to be specified for parsing.")
        else:
            self._model_cls = model_cls

        if "default" not in kwargs:
            kwargs["default"] = model_cls.generate_default()

        super().__init__(key, **kwargs)

    @property
    def model_cls(self):
        return self._model_cls

    @property
    def expected_types(self):
        return self.model_cls

    @classmethod
    def none_obj(cls):
        return None

    def _cast_to_desired_type_(self, value):
        return self.desired_type(**value, from_db=True)
