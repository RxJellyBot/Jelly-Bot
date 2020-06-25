from abc import ABC
from dataclasses import dataclass

from models import Model
from models.field import ModelField

__all__ = ["BattleObject", "BattleObjectModel", "BattleObjectModelField"]


@dataclass
class BattleObject(ABC):
    pass


class BattleObjectModelField(ModelField):
    def __init__(self, key, **kwargs):
        super().__init__(key, BattleObjectModel, **kwargs)

    @property
    def expected_types(self):
        return super().expected_types + tuple(BattleObjectModel.__subclasses__())


class BattleObjectModel(Model, ABC):
    """
    Base battle object including character, chest, monsters and field bosses.
    """
    pass
