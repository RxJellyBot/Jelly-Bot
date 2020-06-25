from extutils.flags import FlagCodeEnum

__all__ = ["GameCreationResult", "GameMapSetResult", "GameReadyResult", "GameStartResult"]


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
    X_GAME_NOT_FOUND = 102


class GameReadyResult(FlagCodeEnum):
    """
    Result of setting the ready status of a pending game.
    """
    O_UPDATED = -1

    X_PLAYER_NOT_FOUND = 101
    X_GAME_NOT_FOUND = 102


class GameStartResult(FlagCodeEnum):
    """
    Result of starting a game.
    """
    O_STARTED = -1

    X_GAME_NOT_READY = 101
    X_GAME_NOT_FOUND = 102
    X_GAME_EXISTED = 103
