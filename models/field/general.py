from ._base import BaseField


class GeneralField(BaseField):
    def __init__(self, key, **kwargs):
        """
        Default Properties Overrided:

        - ``allow_none`` - **Always** ``True`` because ``none_obj()`` is already ``None``.

        .. seealso::
            Check the document of :class:`BaseField` for other default properties.
        """
        if not kwargs.get("allow_none", True):
            from mongodb.utils.logger import logger
            logger.logger.warning(f"This `GenericField` (Key: {key}) will always allow `None`.")
        kwargs["allow_none"] = True

        if "auto_cast" not in kwargs:
            kwargs["auto_cast"] = False

        super().__init__(key, **kwargs)

    @classmethod
    def none_obj(cls):
        return None

    @property
    def expected_types(self):
        return str, bool, int, list, dict
