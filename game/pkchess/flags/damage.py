from extutils.flags import FlagCodeEnum

__all__ = ("DamageType",)


class DamageType(FlagCodeEnum):
    """Flags of the damage type."""
    MISSED = -2
    BLOCKED = -1

    DEALT = 1 << 0
    CRITICAL = 1 << 1
    SKILL = 1 << 2

    @property
    def damage_dealt(self):
        return self.code > 0
