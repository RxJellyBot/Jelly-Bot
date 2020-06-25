from dataclasses import dataclass, field
from typing import List

from game.pkchess.objbase import BattleObject
from .base import CharacterTemplate

__all__ = ["Character"]


@dataclass
class Character(BattleObject):
    template: CharacterTemplate

    name: str = field(init=False)

    HP: int = field(init=False)
    MP: int = field(init=False)

    ATK: int = field(init=False)
    DEF: int = field(init=False)
    CRT: float = field(init=False)

    ACC: float = field(init=False)
    EVD: float = field(init=False)

    MOV: float = field(init=False)

    skill_ids: List[int] = field(init=False)

    EXP: int = 0

    def __post_init__(self):
        self.name = self.template.name

        self.HP = self.template.HP
        self.MP = self.template.MP

        self.ATK = self.template.ATK
        self.DEF = self.template.DEF
        self.CRT = self.template.CRT

        self.ACC = self.template.ACC
        self.EVD = self.template.EVD

        self.MOV = self.template.MOV

        self.skill_ids = self.template.skill_ids

    # TODO: Game - function to increase exp and grow the parameter if EXP passing certain threshold
