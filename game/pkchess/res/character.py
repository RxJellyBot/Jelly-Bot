from typing import Dict

from game.pkchess.character import CharacterTemplate

__all__ = ["character_templates"]

character_templates: Dict[str, CharacterTemplate] = {
    "nearnox": CharacterTemplate(
        "Nearnox",
        HP=1000, HP_growth=100, MP=750, MP_growth=20,
        ATK=105, ATK_growth=20, DEF=100, DEF_growth=3, CRT=0.05, CRT_growth=0.01,
        ACC=50, ACC_growth=10, EVD=10, EVD_growth=1, MOV=3, MOV_growth=0.15,
        skill_ids=[110001, 200001, 200002, 210001]
    )
}
"""
Characters for the players to pick.

Key is the name of the character with the letters all in lower case for case-insensitivity.
"""
