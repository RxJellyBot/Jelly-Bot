from abc import ABC

from models import Model
from models.field import ModelField

__all__ = ["BattleObject", "BattleObjectField"]


class BattleObjectField(ModelField):
    def __init__(self, key, **kwargs):
        super().__init__(key, BattleObject, **kwargs)

    @property
    def expected_types(self):
        return super().expected_types + tuple(BattleObject.__subclasses__())


class BattleObject(Model, ABC):
    """
    Base battle object including character, chest, monsters and field bosses.
    """
    pass
