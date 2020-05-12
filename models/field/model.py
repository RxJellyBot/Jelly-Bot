from ._base import BaseField
from .exceptions import FieldModelClassInvalid


class ModelField(BaseField):
    # noinspection PyUnresolvedReferences
    def __init__(self, key, model_cls, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - **Always** ``True`` because ``none_obj()`` is already ``None``
        - ``auto_cast`` - **Always** ``True`` to ensure this field yields ``Model``
        - ``default`` - default model of ``model_cls``

        :raises ValueError: if `model_cls` is `None`
        :raises FieldModelClassInvalid: if `model_cls` is not inherit from `models.Model`

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        from models import Model

        if model_cls is None:
            raise ValueError("`model_cls` needs to be specified for parsing.")
        elif not isinstance(model_cls, type) or not issubclass(model_cls, Model):
            raise FieldModelClassInvalid(key, model_cls)

        self._model_cls = model_cls

        if not kwargs.get("auto_cast", True):
            from mongodb.utils.logger import logger
            logger.logger.warning(f"`autocast` of this `ModelField` (Key: {key}) is always `True`.")
        kwargs["auto_cast"] = True

        if "default" not in kwargs:
            kwargs["default"] = model_cls.generate_default()

        super().__init__(key, **kwargs)

    @property
    def model_cls(self):
        return self._model_cls

    @property
    def expected_types(self):
        return self.model_cls, dict

    @classmethod
    def none_obj(cls):
        return None

    def _cast_to_desired_type_(self, value):
        # noinspection PyUnresolvedReferences
        return self.desired_type.cast_model(value)
