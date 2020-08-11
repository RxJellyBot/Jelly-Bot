"""
The module contains the "loaded" skills in the variable ``skill``.
"""
from typing import Dict

from django.utils.translation import gettext_lazy as _

from game.pkchess.skill import Skill

__all__ = ["skills"]

skills: Dict[int, Skill] = {
    110001: Skill(110001, _("Normal Attack #1"), 0, 100, 0, {(0, 1)}),
    200001: Skill(200001, _("Cross Slash"), 50, 200, 2, {(-1, 0), (0, -1), (1, 0), (0, 1)}),
    200002: Skill(200002, _("X Slash"), 50, 200, 2, {(-1, -1), (1, -1), (-1, 1), (1, 1)}),
    210001: Skill(210001, _("God's hammer"), 150, 600, 5, {(-1, 1), (0, 1), (1, 1), (-1, 2), (0, 2), (1, 2)})
}
"""
Skills for characters to use.

The key of this skill dict represents the ID of the corresponding skill.
"""
