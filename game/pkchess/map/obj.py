from dataclasses import dataclass
from typing import List, Dict, Optional

from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.objbase import BattleObject

__all__ = ["MapPoint", "MapCoordinate", "Map"]


@dataclass
class MapCoordinate:
    """
    Represents the coordinate of a map point.
    """
    X: int
    Y: int


@dataclass
class MapPoint:
    """
    Represents a map point.
    """
    status: MapPointStatus
    coord: MapCoordinate
    obj: Optional[BattleObject] = None


@dataclass
class Map:
    """
    Represents the map.
    """
    width: int
    height: int
    points: List[List[MapPoint]]
    resources: Dict[MapPointResource, List[MapCoordinate]]

    @property
    def points_flattened(self) -> List[MapPoint]:
        """
        Get the 1D array of the points flattened from ``self.points``.

        :return: flattened array of `self.points`

        .. seealso::
            https://stackoverflow.com/a/29244327/11571888
        """
        return sum(self.points, [])
