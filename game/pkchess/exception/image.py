from abc import ABC

__all__ = ["MapImageError", "PlayerIconNotExistsError"]


class MapImageError(ABC, Exception):
    pass


class PlayerIconNotExistsError(MapImageError):
    pass
