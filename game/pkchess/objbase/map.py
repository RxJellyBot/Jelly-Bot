from dataclasses import dataclass
from typing import List

from models import Model, ModelDefaultValueExt
from models.field import IntegerField, MultiDimensionalArrayField, FlagField, ModelField, ArrayField
from extutils.flags import FlagSingleEnum
from game.pkchess.objbase import BattleObject
from game.pkchess.exception import MapTooFewPointsError, MapDimensionTooSmallError
from strres.game_pk import MapPoint

__all__ = ["MapPointStatus", "MapPointResource", "MapPointModel", "MapCoordinateModel", "MapModel", "MapTemplate"]


# region Enums / Flags

class MapPointStatus(FlagSingleEnum):
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

    UNAVAILABLE = 0, MapPoint.UNAVAILABLE
    EMPTY = 1, MapPoint.EMPTY
    PLAYER = 2, MapPoint.PLAYER
    CHEST = 3, MapPoint.CHEST
    MONSTER = 4, MapPoint.MONSTER
    FIELD_BOSS = 5, MapPoint.FIELD_BOSS


class MapPointResource(FlagSingleEnum):
    """
    Deployable reource type of the map point.

    ``CHEST`` - Chest could be deployed on the map point.
    ``MONSTER`` - Monster could be deployed on the map point.
    ``FIELD_BOSS`` - Field boss could be deployed on the map point.
    """
    CHEST = 1, MapPoint.CHEST
    MONSTER = 2, MapPoint.MONSTER
    FIELD_BOSS = 3, MapPoint.FIELD_BOSS


# endregion


# region Special model field

class MapPointStatusField(FlagField):
    FLAG_TYPE = MapPointStatus


class BattleObjectField(ModelField):
    def __init__(self, key, **kwargs):
        super().__init__(key, BattleObject, **kwargs)

    @property
    def expected_types(self):
        return super().expected_types + tuple(BattleObject.__subclasses__())


# endregion


# region Models

class MapCoordinateModel(Model):
    """
    Map point coordinate to be stored in the database under ``MapPointModel.Coord``.
    """
    WITH_OID = False

    X = IntegerField("x", default=ModelDefaultValueExt.Required)
    Y = IntegerField("y", default=ModelDefaultValueExt.Required)


class MapPointModel(Model):
    """
    Map point to be stored in the database under ``MapModel.PointStatus``.
    """
    WITH_OID = False

    PointStatus = MapPointStatusField("s", default=ModelDefaultValueExt.Required)
    Obj = BattleObjectField("obj", default=None)
    Coord = ModelField("c", MapCoordinateModel, default=ModelDefaultValueExt.Required)
    Resource = ArrayField("res", MapPointResource)


class MapModel(Model):
    Width = IntegerField("w", positive_only=True, default=ModelDefaultValueExt.Required)
    Height = IntegerField("h", positive_only=True, default=ModelDefaultValueExt.Required)
    PointStatus = MultiDimensionalArrayField("pt", 2, MapPointModel, default=ModelDefaultValueExt.Required)


# endregion


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
    """
    ``int`` of the point corresponds to :class:`MapPointStatus`
    
    The reason of using ``int`` instead of :class:`MapPointStatus` is to make the visualization of the map to be easier
    """
    points: List[List[int]]

    def __post_init__(self):
        if self.width < MapTemplate.MIN_WIDTH or self.height < MapTemplate.MIN_HEIGHT:
            raise MapDimensionTooSmallError()

        available_nodes = sum(sum([1 if p > 0 else 0 for p in row]) for row in self.points)
        if available_nodes < MapTemplate.MIN_AVAILABLE_NODES:
            raise MapTooFewPointsError(MapTemplate.MIN_AVAILABLE_NODES, available_nodes)

        # TODO: Move to model construction
        # for y in range(self.height):
        #     row: List[MapPoint] = []
        #
        #     for x in range(self.width):
        #         p_type = MapPointStatus.cast(self.points[x][y])
        #
        #         row.append(MapPoint(p_type, None, MapCoordinate(x, y)))
        #
        #     self.point_status.append(row)

    def tighten(self):
        pass  # TODO TEST

    def deploy_object(self):
        pass  # TODO TEST

    def draw_image(self):
        pass  # TODO TEST

    def to_model(self):
        pass  # TODO TEST

    @staticmethod
    def load_from_file(path: str) -> 'MapTemplate':
        """
        Load the template from a file.

        -----

        **About the file format**

        The map file to be parsed should have the specifications below:

        - A rectangle with its content being a single digit number, representing the initial :class:`MapPointStatus`.

        - End with an empty line.

        Example file::

            1111
            1121
            1211
            1111
            (empty new line)

        :param path: path of the file
        :return: a parsed `MapTemplate`
        """
        points: List[List[int]] = []

        with open(path) as f:
            for line in f.readlines():
                points.append([int(n) for n in line[:-1]])

        return MapTemplate(len(points[0]), len(points), points)
