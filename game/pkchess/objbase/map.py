from dataclasses import dataclass
from typing import List, Dict

from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.exception import (
    MapTooFewPointsError, MapDimensionTooSmallError, MapShapeMismatchError,
    MapPointUnspawnableError, SpawnPointOutOfMapError, NoPlayerSpawnPointError, UnknownResourceTypeError
)
from game.pkchess.mdls import MapPointModel, MapCoordinateModel, MapModel

__all__ = ["MapTemplate"]


@dataclass
class MapTemplate:
    """
    Map template.

    This could be converted to :class:`MapModel` and
    store to the database (initialize a game) by calling `to_model()`.
    """
    MIN_WIDTH = 9
    MIN_HEIGHT = 9
    MIN_AVAILABLE_NODES = 81

    width: int
    height: int
    points: List[List[MapPointStatus]]
    resources: Dict[MapPointResource, List[MapCoordinateModel]]

    def __post_init__(self):
        if self.width < MapTemplate.MIN_WIDTH or self.height < MapTemplate.MIN_HEIGHT:
            raise MapDimensionTooSmallError()

        available_nodes = sum(sum(1 if p.is_map_point else 0 for p in row) for row in self.points)
        if available_nodes < MapTemplate.MIN_AVAILABLE_NODES:
            raise MapTooFewPointsError(MapTemplate.MIN_AVAILABLE_NODES, available_nodes)

        if not any(any(p == MapPointStatus.PLAYER for p in row) for row in self.points):
            raise NoPlayerSpawnPointError()

        # Check resource points
        for coords in self.resources.values():
            for coord in coords:
                x = coord.x
                y = coord.y

                # Check out of map
                if x >= self.width or y >= self.height:
                    raise SpawnPointOutOfMapError()

                if not self.points[x][y].is_map_point:
                    raise MapPointUnspawnableError()

        # Check dimension and point matrix match
        try:
            self.points[self.width - 1][self.height - 1]
        except IndexError:
            raise MapShapeMismatchError()

    def tighten(self):
        pass  # TODO TEST

    def respawn(self):
        pass  # TODO TEST

    def to_model(self) -> MapModel:
        pts = []

        for x, pts_arr in enumerate(self.points):
            arr = []

            for y, pt in enumerate(pts_arr):
                arr.append(MapPointModel(Status=pt, Coord=MapCoordinateModel(X=x, Y=y)))

            pts.append(arr)

        return MapModel(Width=self.width, Height=self.height, Points=pts, Resources=self.resources)

    @staticmethod
    def load_from_file(path: str) -> 'MapTemplate':
        """
        Load the template from a map file.

        This parsing method checks logic error, but not the format error.

        .. seealso::
            See `res/map/spec.md` for the specification of the map file.

        :param path: path of the file
        :return: a parsed `MapTemplate`
        """
        with open(path) as f:
            lines = f.read().split("\n")

        # Parse dimension
        width, height = [int(n) for n in lines.pop(0).split(" ", 2)]

        # Parse initial map points
        points: List[List[MapPointStatus]] = [[] for _ in range(width)]
        for y in range(height):
            for x, elem in zip(range(width), lines.pop(0)):
                points[x].append(MapPointStatus.cast(elem))

        # parse resource spawning location
        res_dict: Dict[MapPointResource, List[MapCoordinateModel]] = {}
        for line in lines:
            type_int, *coords = line.split(" ")

            try:
                res_type = MapPointResource.cast(type_int)
            except ValueError:
                raise UnknownResourceTypeError()

            coords = [coord.split(",", 2) for coord in coords]
            res_dict[res_type] = [MapCoordinateModel(X=int(x), Y=int(y)) for x, y in coords]

        return MapTemplate(width, height, points, res_dict)
