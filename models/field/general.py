from ._base import BaseField


class GeneralField(BaseField):
    def __init__(self, key, **kwargs):
        """
        ``allow_none`` is always ``True`` because the `None` object for this field is `None`.
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
