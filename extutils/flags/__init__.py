"""Module of extended ``Enum``, ``Flag``, which could be used in a lot of situations."""
from .main import (
    DuplicatedCodeError,
    FlagCodeEnum, FlagSingleEnum, FlagDoubleEnum, FlagPrefixedDoubleEnum, FlagOutcomeMixin,
    is_flag_class, is_flag_single, is_flag_double, is_flag_instance
)
from .mongo import type_registry
