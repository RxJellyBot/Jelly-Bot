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
    X_PLAYER_NOT_EXISTS = 104

    X_TOO_MANY_MOVES = 201
    X_ALREADY_PERFORMED = 202
    X_DESTINATION_NOT_EMPTY = 203
    X_DESTINATION_OUT_OF_MAP = 204
    X_MOVE_PATH_NOT_FOUND = 205

    X_SKILL_IDX_OUT_OF_BOUND = 301
    X_SKILL_NOT_FOUND = 302
