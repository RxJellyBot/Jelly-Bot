from ._base import BaseField


class DictionaryField(BaseField):
    def __init__(self, key, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - ``False``

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False

        super().__init__(key, **kwargs)

    @classmethod
    def none_obj(cls):
        return {}

    @property
    def expected_types(self):
        return dict,
