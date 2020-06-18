from typing import Type, Dict, Tuple, Any

from game.pkchess.objbase import (
    MapTemplate, MapPointStatus, MapPointResource, MapCoordinateModel, MapPointModel, MapModel
)
from game.pkchess.obj import Character
from game.pkchess.exception import MapTooFewPointsError, MapDimensionTooSmallError
from models import Model
from tests.base import TestCase, TestModel

__all__ = ["TestMapTemplate", "TestMapCoordianteModel", "TestMapPointModel", "TestMapModel"]


class TestMapTemplate(TestCase):
    def test(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        MapTemplate(w, h, [[MapPointStatus.EMPTY.code for _ in range(w)] for _ in range(h)])

    def test_insuf_width(self):
        w = MapTemplate.MIN_WIDTH - 1
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(MapDimensionTooSmallError):
            MapTemplate(w, h, [[MapPointStatus.EMPTY.code for _ in range(w)] for _ in range(w)])

    def test_insuf_height(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT - 1

        with self.assertRaises(MapDimensionTooSmallError):
            MapTemplate(w, h, [[MapPointStatus.EMPTY.code for _ in range(w)] for _ in range(h)])

    def test_insuf_points(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(MapTooFewPointsError):
            MapTemplate(w, h,
                        [[MapPointStatus.EMPTY.code for _ in range(w)] for _ in range(h - 2)]
                        + [[MapPointStatus.UNAVAILABLE.code for _ in range(w)] + [MapPointStatus.PLAYER.code for _ in
                                                                                  range(w)]])

    def test_parse_file(self):
        mt = MapTemplate.load_from_file("tests/res/game_pkchess/map")

        self.assertEqual(mt.width, 9)
        self.assertEqual(mt.height, 9)
        self.assertEqual(
            mt.points,
            [
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [2, 2, 2, 2, 2, 2, 2, 2, 2],
                [3, 3, 3, 3, 3, 3, 3, 3, 3],
                [4, 4, 4, 4, 4, 4, 4, 4, 4],
                [5, 5, 5, 5, 5, 5, 5, 5, 5]
            ]
        )


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
            ("s", "PointStatus"): MapPointStatus.CHEST,
            ("c", "Coord"): MapCoordinateModel(X=1, Y=7)
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("obj", "Obj"): (None, Character()),
            ("res", "Resource"): ([], [MapPointResource.CHEST, MapPointResource.MONSTER])
        }


class TestMapModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return MapModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("w", "Width"): 2,
            ("h", "Height"): 2,
            ("pt", "PointStatus"): [
                [MapPointModel(PointStatus=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=0)),
                 MapPointModel(PointStatus=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=1))],
                [MapPointModel(PointStatus=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=0)),
                 MapPointModel(PointStatus=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=1))]
            ]
        }
