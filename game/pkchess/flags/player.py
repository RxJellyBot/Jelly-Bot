from extutils.flags import FlagCodeEnum

__all__ = ["PlayerAction", "PlayerActionResult"]


class PlayerAction(FlagCodeEnum):
    """
    Type of player actions in a single turn.
    """
    MOVE = 1
    SKILL_1 = 11
    SKILL_2 = 12


class PlayerActionResult(FlagCodeEnum):
    """
    Type of player actions in a single turn.
    """
    O_ACTED = -1

    X_GAME_NOT_STARTED = 101
    X_GAME_NOT_FOUND = 102
    X_PLAYER_NOT_CURRENT = 103
    X_TOO_MANY_MOVES = 104
    X_PLAYER_NOT_EXISTS = 105
    X_DESTINATION_NOT_EMPTY = 106
    X_DESTINATION_OUT_OF_MAP = 107

    X_ALREADY_MOVED = 201
