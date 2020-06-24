from extutils.flags import FlagCodeEnum

__all__ = ["GameCreationResult", "GameMapSetResult"]


class GameCreationResult(FlagCodeEnum):
    """
    Result of a pending game creation.
    """
    O_CREATED = -2
    O_JOINED = -1

    X_ALREADY_JOINED = 101
    X_CHARACTER_NOT_EXIST = 102


class GameMapSetResult(FlagCodeEnum):
    """
    Result of setting the map to be used to a pending game.
    """
    O_SET = -1

    X_TEMPLATE_NOT_FOUND = 101
