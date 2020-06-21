from abc import ABC

from models import Model

__all__ = ["BattleObject"]


class BattleObject(Model, ABC):
    """
    Base battle object including character, chest, monsters and field bosses.
    """
    pass
