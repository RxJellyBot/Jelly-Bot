from ._base import BaseField


class GeneralField(BaseField):
    def __init__(self, key, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - **Always** ``True`` because ``none_obj()`` is already ``None``.

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if "auto_cast" not in kwargs:
            kwargs["auto_cast"] = False

        super().__init__(key, **kwargs)

    def none_obj(self):
        return None

    @property
    def expected_types(self):
        return str, bool, int, list, dict
