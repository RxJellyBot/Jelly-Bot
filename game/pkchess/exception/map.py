from abc import ABC

__all__ = ["MapError", "MapTooFewPointsError", "MapDimensionTooSmallError", "MapShapeMismatchError",
           "MapPointError", "MapPointUnspawnableError", "SpawnPointOutOfMapError", "UnknownResourceTypeError",
           "NoPlayerSpawnPointError", "MapTooManyPlayersError", "CoordinateOutOfBoundError",
           "PlayerDeployedOnUndeployableError", "CenterOutOfMapError", "PathNotFoundError", "PathSameDestinationError",
           "PathEndOutOfMapError"]


class MapError(ABC, Exception):
    pass


class MapPointError(MapError, ABC):
    pass


class MapPathError(MapError, ABC):
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


class PathNotFoundError(MapPathError):
    def __init__(self, origin, destination):
        super().__init__(f"Path from {origin} to {destination} not found")


class PathSameDestinationError(MapPathError):
    def __init__(self):
        super().__init__("Origin and the destination are the same")


class PathEndOutOfMapError(MapPathError):
    def __init__(self, origin, destination, map_width, map_height):
        super().__init__(f"Either origin {origin} or destination {destination} is out of map / "
                         f"Map width: {map_width} height: {map_height}")


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


class CenterOutOfMapError(MapPointError):
    pass
