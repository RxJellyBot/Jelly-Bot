from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.objbase import BattleObject
from game.pkchess.map import Map, MapPoint, MapCoordinate
from models import Model, ModelDefaultValueExt
from models.field import IntegerField, MultiDimensionalArrayField, FlagField, ModelField, DictionaryField

__all__ = ["MapPointModel", "MapCoordinateModel", "MapModel"]


class MapPointStatusField(FlagField):
    FLAG_TYPE = MapPointStatus


class BattleObjectField(ModelField):
    def __init__(self, key, **kwargs):
        super().__init__(key, BattleObject, **kwargs)

    @property
    def expected_types(self):
        return super().expected_types + tuple(BattleObject.__subclasses__())


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

    Status = MapPointStatusField("s", default=ModelDefaultValueExt.Required)
    Coord = ModelField("c", MapCoordinateModel, default=ModelDefaultValueExt.Required)
    Obj = BattleObjectField("obj", default=None)


class MapModel(Model):
    Width = IntegerField("w", positive_only=True, default=ModelDefaultValueExt.Required)
    Height = IntegerField("h", positive_only=True, default=ModelDefaultValueExt.Required)
    Points = MultiDimensionalArrayField("pt", 2, MapPointModel, default=ModelDefaultValueExt.Required)
    Resources = DictionaryField("res", default=ModelDefaultValueExt.Required)

    def to_map(self) -> Map:
        pts = []

        # Convert `points`
        for x, pts_arr in enumerate(self.points):
            arr = []

            for y, pt in enumerate(pts_arr):
                arr.append(MapPoint(pt.status, MapCoordinate(pt.coord.x, pt.coord.y)))

            pts.append(arr)

        # Convert `resources`
        res = dict(self.resources)
        for k, v in self.resources.items():
            res[MapPointResource.cast(k)] = [MapCoordinate(coord[MapCoordinateModel.X.key],
                                                           coord[MapCoordinateModel.Y.key]) for coord in v]

        return Map(self.width, self.height, pts, res)
