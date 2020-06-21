from game.pkchess.flags import MapPointStatus
from game.pkchess.objbase import BattleObject
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
    Obj = BattleObjectField("obj", default=None)
    Coord = ModelField("c", MapCoordinateModel, default=ModelDefaultValueExt.Required)


class MapModel(Model):
    Width = IntegerField("w", positive_only=True, default=ModelDefaultValueExt.Required)
    Height = IntegerField("h", positive_only=True, default=ModelDefaultValueExt.Required)
    Points = MultiDimensionalArrayField("pt", 2, MapPointModel, default=ModelDefaultValueExt.Required)
    Resources = DictionaryField("res", default=ModelDefaultValueExt.Required)
