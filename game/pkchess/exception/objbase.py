from abc import ABC


class MapException(ABC, Exception):
    pass


class MapTooFewPointsError(MapException):
    def __init__(self, expected: int, actual: int):
        super().__init__(f"{actual} / {expected}")


class MapDimensionTooSmallError(MapException):
    pass
