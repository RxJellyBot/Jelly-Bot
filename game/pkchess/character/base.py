from dataclasses import dataclass
from typing import List

__all__ = ["CharacterTemplate"]


@dataclass
class CharacterTemplate:
    name: str

    HP: int
    HP_growth: int
    MP: int
    MP_growth: int

    ATK: int
    ATK_growth: int
    DEF: int
    DEF_growth: int
    CRT: float
    CRT_growth: float

    ACC: float
    ACC_growth: float
    EVD: float
    EVD_growth: float

    MOV: float
    MOV_growth: float

    skill_ids: List[int]
