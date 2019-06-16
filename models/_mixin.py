class CreateDefaultMixin:
    # noinspection PyUnresolvedReferences, PyArgumentList
    @classmethod
    def create_default(cls):
        inst = cls(**{k: v for k, v in cls.default_vals}, from_db=True, incl_oid=False)
        return inst
