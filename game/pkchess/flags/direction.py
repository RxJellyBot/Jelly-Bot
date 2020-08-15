from typing import Tuple, Set

from extutils.flags import FlagSingleEnum
from game.pkchess.exception import UnhandledSkillDirectionError

__all__ = ("SkillDirection",)


class SkillDirection(FlagSingleEnum):
    """Direction to use the skill."""
    UP = 1, "U"
    RIGHT = 2, "R"
    DOWN = 3, "D"
    LEFT = 4, "L"

    TEST = -1, ""

    def rotate_offsets(self, offsets: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        if self == SkillDirection.UP:
            return offsets

        if self == SkillDirection.DOWN:
            return {(-x, -y) for x, y in offsets}

        if self == SkillDirection.RIGHT:
            return {(y, -x) for x, y in offsets}

        if self == SkillDirection.LEFT:
            return {(-y, x) for x, y in offsets}

        raise UnhandledSkillDirectionError(self)
