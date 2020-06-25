from typing import Type, Tuple, Dict, Any

from bson import ObjectId

from game.pkchess.character import CharacterModel
from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.map import Map, MapPoint, MapCoordinate, MapModel, MapPointModel, MapCoordinateModel
from game.pkchess.res import get_map_template
from models import Model
from tests.base import TestModel

__all__ = ["TestMapCoordianteModel", "TestMapPointModel", "TestMapModel"]


class TestMapCoordianteModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return MapCoordinateModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("x", "X"): 1,
            ("y", "Y"): 10
        }


class TestMapPointModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return MapPointModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("s", "Status"): MapPointStatus.CHEST,
            ("c", "Coord"): MapCoordinateModel(X=1, Y=7)
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("obj", "Obj"): (None, CharacterModel())
        }


class TestMapModel(TestModel.TestClass):
    PLAYER_OID = ObjectId()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return MapModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("w", "Width"): 2,
            ("h", "Height"): 2,
            ("pt", "Points"): [
                [MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=0)),
                 MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=1))],
                [MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=0)),
                 MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=1))]
            ],
            ("res", "Resources"): {
                MapPointResource.CHEST: [MapCoordinateModel(X=0, Y=0), MapCoordinateModel(X=1, Y=1)]
            },
            ("t", "TemplateName"): "map01",
            ("plyr", "PlayerLocation"): {cls.PLAYER_OID: MapCoordinateModel(X=1, Y=0)}
        }

    def test_to_map(self):
        actual_map = MapModel(
            Width=2, Height=2,
            Points=[
                [MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=0)),
                 MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=1))],
                [MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=0)),
                 MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=1))]
            ],
            Resources={
                MapPointResource.CHEST: [MapCoordinateModel(X=0, Y=0), MapCoordinateModel(X=1, Y=1)]
            },
            TemplateName="map01", PlayerLocation={self.PLAYER_OID: MapCoordinateModel(X=1, Y=0)}
        ).to_map()

        expected_map = Map(
            2, 2,
            [[MapPoint(MapPointStatus.EMPTY, MapCoordinate(x, y)) for y in range(2)] for x in range(2)],
            {MapPointResource.CHEST: [MapCoordinate(0, 0), MapCoordinate(1, 1)]},
            get_map_template("map01"), player_location={self.PLAYER_OID: MapCoordinate(1, 0)}
        )

        self.assertEqual(expected_map.width, actual_map.width)
        self.assertEqual(expected_map.height, actual_map.height)
        self.assertEqual(expected_map.points, actual_map.points)
        self.assertEqual(expected_map.resources, actual_map.resources)
