from dataclasses import dataclass
from typing import Set, Tuple

__all__ = ("Skill",)


@dataclass
class Skill:
    """
    Represents a skill.

    -----

    **Range**

    ``range`` is a collection of the coordinate offset in the format of ``(X offset, Y offset)``.

    Each offsets assumes the player is heading top side.

    The coordinate of the player itself is at ``(0, 0)``.

    If the range is {(0, 1), (1, 0)},
    it means the skill covers the immediate right and the immediate top point related to the character.

    For both X and Y, positive values means top/right; negative values means left/bottom.

    -----

    **ID**

    ID is a 6 digits number.

    The 1st digit have the following meanings correspond to its digit:

    +-------+-----------------------------------------------------------------------------------------------+
    | digit | description                                                                                   |
    +-------+-----------------------------------------------------------------------------------------------+
    |   1   | Normal attack. Not consuming MP and does not have cooldown.                                   |
    +-------+-----------------------------------------------------------------------------------------------+
    |   2   | Normal skill. Consumes small portion of MP and has a short cooldown.                          |
    +-------+-----------------------------------------------------------------------------------------------+
    |   3   | Ultimate skill. Consumes more MP and has a longer cooldown.                                   |
    +-------+-----------------------------------------------------------------------------------------------+
    |   9   | God skill. Consumes a lot MP and can be used only once(almost) in a game (infinite cooldown.) |
    +-------+-----------------------------------------------------------------------------------------------+

    The 2nd digit have the following meanings correspond to its digit:

    +-------+----------------------+
    | digit | description          |
    +-------+----------------------+
    |   0   | Undirectional skill. |
    +-------+----------------------+
    |   1   | Directional skill.   |
    +-------+----------------------+
    |   2   | Global skill.        |
    +-------+----------------------+

    The 3rd~6th digit is the sequential ID of the skill.
    """
    id: int

    name: str

    mp_cost: int
    power: int
    cooldown: int

    range: Set[Tuple[int, int]]
