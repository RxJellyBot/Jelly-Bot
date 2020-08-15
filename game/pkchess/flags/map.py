from extutils.flags import FlagCodeEnum

__all__ = ("MapPointStatus", "MapPointResource",)


class MapPointStatus(FlagCodeEnum):
    """
    Type of the map point.

    ``UNAVAILABLE`` - The map point is unavailable for the map.
    ``EMPTY`` - The map point is empty.
    ``PLAYER`` - A player is on the map point.
    ``CHEST`` - A chest is on the map point.
    ``MONSTER`` - A monster is on the map point.
    ``FIELD_BOSS`` - A field boss is on the map point.
    """

    @classmethod
    def default(cls):
        return MapPointStatus.UNAVAILABLE

    UNAVAILABLE = 0
    EMPTY = 1
    PLAYER = 2
    CHEST = 3
    MONSTER = 4
    FIELD_BOSS = 5

    @property
    def is_map_point(self):
        return self.code > 0


class MapPointResource(FlagCodeEnum):
    """
    Deployable resource type of the map point.

    ``CHEST`` - Chest could be spawned on the map point.
    ``MONSTER`` - Monster could be spawned on the map point.
    ``FIELD_BOSS`` - Field boss could be spawned on the map point.
    """
    CHEST = 3
    MONSTER = 4
    FIELD_BOSS = 5
