from abc import ABC

__all__ = ["MapError", "MapTooFewPointsError", "MapDimensionTooSmallError", "MapShapeMismatchError",
           "MapPointError", "MapPointUnspawnableError", "SpawnPointOutOfMapError", "UnknownResourceTypeError",
           "NoPlayerSpawnPointError", "MapTooManyPlayersError", "CoordinateOutOfBoundError",
           "PlayerDeployedOnUndeployableError"]


class MapError(ABC, Exception):
    pass


class MapPointError(MapError, ABC):
    pass


class MapTooFewPointsError(MapError):
    def __init__(self, expected: int, actual: int):
        super().__init__(f"{actual} / {expected}")


class MapTooManyPlayersError(MapError):
    def __init__(self, max_player: int, actual_player: int):
        super().__init__(f"{actual_player} / {max_player}")


class MapDimensionTooSmallError(MapError):
    pass


class MapShapeMismatchError(MapError):
    pass


class MapPointUnspawnableError(MapPointError):
    pass


class PlayerDeployedOnUndeployableError(MapPointError):
    pass


class SpawnPointOutOfMapError(MapPointError):
    pass


class UnknownResourceTypeError(MapPointError):
    pass


class NoPlayerSpawnPointError(MapPointError):
    pass


class CoordinateOutOfBoundError(MapPointError):
    pass
