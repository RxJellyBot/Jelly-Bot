from abc import ABC

__all__ = [
    "DamageError", "DamageFalseNegativeError", "DamageFalsePositiveError", "DamageTypeInvalidError",
    "DamageValueNegativeError", "SkillPowerNegativeError"
]


class DamageError(ABC, Exception):
    pass


class DamageFalseNegativeError(DamageError, ValueError):
    def __init__(self, damage_type_code: int, damage_dealt: float):
        super().__init__(f"Damage value ({damage_dealt}) indicated that the damage was dealt "
                         f"but the type code ({damage_type_code}) indicates that it was not.")


class DamageFalsePositiveError(DamageError, ValueError):
    def __init__(self, damage_type_code: int, damage_dealt: float):
        super().__init__(f"Damage value ({damage_dealt}) indicated that the damage was not dealt "
                         f"but the type code ({damage_type_code}) indicates that it was.")


class DamageTypeInvalidError(DamageError):
    def __init__(self):
        super().__init__("Damage type code should not be 0.")


class DamageValueNegativeError(DamageError, ValueError):
    def __init__(self, damage_dealt: float):
        super().__init__(f"Value of the damage dealt ({damage_dealt}) should be > 0.")


class SkillPowerNegativeError(DamageError):
    def __init__(self, skill_power: int):
        super().__init__(f"Skill power ({skill_power}) is negative.")
