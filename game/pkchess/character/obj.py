from dataclasses import dataclass, field
from typing import List

from game.pkchess.objbase import BattleObject
from .base import CharacterTemplate

__all__ = ["Character"]


@dataclass
class Character(BattleObject):
    template: CharacterTemplate

    skill_ids: List[int] = field(init=False)

    EXP: int = 0

    def _init(self):
        self.name = self.template.name

        self.HP = self.template.HP
        self.MP = self.template.MP

        self.ATK = self.template.ATK
        self.DEF = self.template.DEF
        self.CRT = self.template.CRT

        self.ACC = self.template.ACC
        self.EVD = self.template.EVD

        self.MOV = self.template.MOV

        # Duplicate the skill ID list
        # so that the skill ID list could be modified for a character and not affecting the template
        self.skill_ids = list(self.template.skill_ids)

    # TODO: Game - function to increase exp and grow the parameter if EXP passing certain threshold
