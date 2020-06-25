__all__ = ["GameError", "GamePreparationError", "GameActionError", "GameNotReadyError", "GameActionSubmittedError",
           "MoveDestinationOutOfMapError", "GamePlayerNotFoundError"]

from abc import ABC


class GameError(ABC, Exception):
    pass


class GamePlayerNotFoundError(GameError):
    pass


class GamePreparationError(GameError, ABC):
    pass


class GameNotReadyError(GamePreparationError):
    pass


class GameActionError(GameError, ABC):
    pass


class GameActionSubmittedError(GameActionError):
    pass


class MoveDestinationOutOfMapError(GameActionError):
    pass
