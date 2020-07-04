from random import Random
from dataclasses import dataclass

from game.pkchess.exception import (
    DamageFalseNegativeError, DamageFalsePositiveError, DamageValueNegativeError, SkillPowerNegativeError,
    DamageTypeInvalidError
)
from game.pkchess.flags import DamageType
from game.pkchess.objbase import BattleObject

__all__ = ["DamageCalculator", "Damage"]


@dataclass
class Damage:
    source: BattleObject
    target: BattleObject

    damage_type_code: int
    damage_dealt: float = 0

    def __post_init__(self):
        if self.damage_type_code == 0:
            raise DamageTypeInvalidError()

        if self.damage_dealt < 0:
            raise DamageValueNegativeError(self.damage_dealt)

        if self.damage_dealt > 0:
            if self.damage_type_code < 0:
                raise DamageFalsePositiveError(self.damage_type_code, self.damage_dealt)

            if not self.is_damage_type(DamageType.DEALT):
                raise DamageFalseNegativeError(self.damage_type_code, self.damage_dealt)

    def is_damage_type(self, damage_type: DamageType) -> bool:
        if damage_type.damage_dealt and self.damage_type_code > 0:
            return self.damage_type_code & damage_type.code > 0
        else:
            return self.damage_type_code == damage_type.code

    @property
    def is_dealt(self):
        return self.is_damage_type(DamageType.DEALT)

    @property
    def is_critical(self):
        return self.is_damage_type(DamageType.CRITICAL)

    @property
    def is_skill(self):
        return self.is_damage_type(DamageType.SKILL)

    @property
    def is_missed(self):
        return self.is_damage_type(DamageType.MISSED)

    @property
    def is_blocked(self):
        return self.is_damage_type(DamageType.BLOCKED)


class DamageCalculator:
    CRT_DMG_RATE = 1.5

    DMG_LOWER_BOUNCE = 0.95
    DMG_UPPER_BOUNCE = 1.05

    RANDOM = Random()

    @classmethod
    def random_hit(cls, rate: float) -> bool:
        return rate > cls.RANDOM.random()

    @classmethod
    def hit_rate(cls, src: BattleObject, tgt: BattleObject) -> float:
        return max(src.ACC - tgt.EVD, 0)

    @classmethod
    def deal_damage(cls, src: BattleObject, tgt: BattleObject, skill_power: int = 100) -> Damage:
        """
        Deals damage for ``src`` to ``tgt``, and return the damage dealing result.

        Damage could be floated around 0.95x ~ 1.05x.

        :param src: damage dealer
        :param tgt: object to be damaged
        :param skill_power: skill power in percentage to be applied on the base damage
        :return: damage dealt
        """
        # Check invalid value
        if skill_power < 0:
            raise SkillPowerNegativeError(skill_power)

        # Calculate base damage
        dmg_base = max(src.ATK - tgt.DEF, 0)
        if dmg_base == 0:
            return Damage(src, tgt, DamageType.BLOCKED.code)

        # Check missed
        if not cls.random_hit(cls.hit_rate(src, tgt)):
            return Damage(src, tgt, DamageType.MISSED.code)

        type_code = DamageType.DEALT.code

        # Apply skill power
        if skill_power != 100:
            dmg_base *= skill_power / 100
            type_code += DamageType.SKILL.code

        # Apply damage floating
        dmg = dmg_base * (cls.DMG_LOWER_BOUNCE + cls.RANDOM.random() * (cls.DMG_UPPER_BOUNCE - cls.DMG_LOWER_BOUNCE))

        # Check critical
        if cls.random_hit(src.CRT):
            dmg *= cls.CRT_DMG_RATE
            type_code += DamageType.CRITICAL.code

        # Deal damage onto the target
        tgt.decrease_hp(dmg)

        return Damage(src, tgt, type_code, dmg)
