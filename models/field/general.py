from ._base import BaseField


class GeneralField(BaseField):
    def __init__(self, key, **kwargs):
        if "allow_none" not in kwargs:
            kwargs["allow_none"] = False
        if "auto_cast" not in kwargs:
            kwargs["auto_cast"] = False

        super().__init__(key, **kwargs)

    @classmethod
    def none_obj(cls):
        return None

    @property
    def expected_types(self):
        return bool, int, list, dict, str
