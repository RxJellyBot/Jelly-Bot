import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from models import Model
from models.field import ModelField

__all__ = ("BattleObject", "BattleObjectModel", "BattleObjectModelField",)


@dataclass
class BattleObject(ABC):
    name: str = field(init=False)

    HP: int = field(init=False)
    HP_MAX: int = field(init=False)
    MP: int = field(init=False)
    MP_MAX: int = field(init=False)

    ATK: float = field(init=False)
    DEF: float = field(init=False)
    CRT: float = field(init=False)

    ACC: float = field(init=False)
    EVD: float = field(init=False)

    MOV: float = field(init=False)

    @abstractmethod
    def _init(self):
        """
        Hook method to initialize the following properties:

        - ``name``

        - ``HP``

        - ``MP``

        - ``ATK``

        - ``DEF``

        - ``CRT``

        - ``ACC``

        - ``EVD``

        - ``MOV``
        """
        pass

    def __post_init__(self):
        self._init()

        self.HP_MAX = self.HP
        self.MP_MAX = self.MP

    @property
    def is_alive(self) -> bool:
        return self.HP > 0

    @property
    def hp_ratio(self) -> float:
        return self.HP / self.HP_MAX

    def decrease_hp(self, dmg: float):
        self.HP = max(self.HP - math.ceil(dmg), 0)


class BattleObjectModelField(ModelField):
    def __init__(self, key, **kwargs):
        super().__init__(key, BattleObjectModel, **kwargs)

    @property
    def expected_types(self):
        return super().expected_types + tuple(BattleObjectModel.__subclasses__())


class BattleObjectModel(Model, ABC):
    """Base battle object including character, chest, monsters and field bosses."""
    pass
