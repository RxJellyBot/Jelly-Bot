from typing import Set, Dict

from bson import ObjectId

from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.objbase import BattleObjectModelField
from game.pkchess.map import Map, MapPoint, MapCoordinate
from game.pkchess.res import get_map_template
from models import Model, ModelDefaultValueExt
from models.field import IntegerField, MultiDimensionalArrayField, FlagField, ModelField, DictionaryField, TextField
from .mixin import ConvertibleMapMixin

__all__ = ["MapPointModel", "MapCoordinateModel", "MapModel"]


class MapPointStatusField(FlagField):
    FLAG_TYPE = MapPointStatus


class MapCoordinateModel(Model):
    """
    Map point coordinate to be stored in the database under ``MapPointModel.Coord``.
    """
    WITH_OID = False

    X = IntegerField("x", default=ModelDefaultValueExt.Required)
    Y = IntegerField("y", default=ModelDefaultValueExt.Required)

    def to_coord(self) -> MapCoordinate:
        return MapCoordinate(self.x, self.y)


class MapPointModel(Model):
    """
    Map point to be stored in the database under ``MapModel.PointStatus``.
    """
    WITH_OID = False

    Status = MapPointStatusField("s", default=ModelDefaultValueExt.Required)
    Coord = ModelField("c", MapCoordinateModel, default=ModelDefaultValueExt.Required)
    Obj = BattleObjectModelField("obj", default=None)


class MapModel(ConvertibleMapMixin, Model):
    """
    A data model represents a game map.
    """
    Width = IntegerField("w", positive_only=True, default=ModelDefaultValueExt.Required)
    Height = IntegerField("h", positive_only=True, default=ModelDefaultValueExt.Required)
    Points = MultiDimensionalArrayField("pt", 2, MapPointModel, default=ModelDefaultValueExt.Required)
    Resources = DictionaryField("res", default=ModelDefaultValueExt.Required)
    TemplateName = TextField("t", default=ModelDefaultValueExt.Required, must_have_content=True)
    PlayerLocation = DictionaryField("plyr", default=ModelDefaultValueExt.Required)

    def to_map(self, players: Set[ObjectId] = None, player_location: Dict[ObjectId, MapCoordinate] = None) -> Map:
        # DRAFT: Game sync - convert battle object on the map point

        # Convert `points`
        pts = []
        for x, pts_arr in enumerate(self.points):
            arr = []

            for y, pt in enumerate(pts_arr):
                arr.append(MapPoint(pt.status, MapCoordinate(pt.coord.x, pt.coord.y)))

            pts.append(arr)

        # Convert player location
        plyr_locn = {}
        for player_oid, coord_model in self.player_location.items():
            plyr_locn[player_oid] = coord_model.to_coord()

        # Convert `resources`
        res = dict(self.resources)
        for k, v in self.resources.items():
            res[MapPointResource.cast(k)] = [MapCoordinate(coord[MapCoordinateModel.X.key],
                                                           coord[MapCoordinateModel.Y.key]) for coord in v]

        return Map(self.width, self.height, pts, res, get_map_template(self.template_name), player_location=plyr_locn)
