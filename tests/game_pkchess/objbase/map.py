from typing import Type, Tuple, Dict, Any

from game.pkchess.exception import (
    MapTooFewPointsError, MapDimensionTooSmallError,
    MapPointUnspawnableError, SpawnPointOutOfMapError, NoPlayerSpawnPointError, UnknownResourceTypeError
)
from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.obj import Character
from game.pkchess.objbase import MapTemplate
from game.pkchess.mdls import MapModel, MapPointModel, MapCoordinateModel
from models import Model
from tests.base import TestCase, TestModel

__all__ = ["TestMapTemplate", "TestMapCoordianteModel", "TestMapPointModel", "TestMapModel"]


class TestMapTemplate(TestCase):
    def test_min_dimension(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(h)] for _ in range(w)], {})

    def test(self):
        w = MapTemplate.MIN_WIDTH + 1
        h = MapTemplate.MIN_HEIGHT + 3

        mt = MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(h)] for _ in range(w)], {})

        self.assertEqual(len(mt.points), w)
        self.assertEqual(len(mt.points[0]), h)
        self.assertEqual(mt.width, w)
        self.assertEqual(mt.height, h)

    def test_point_orientation(self):
        w = MapTemplate.MIN_WIDTH + 1
        h = MapTemplate.MIN_HEIGHT + 3

        mt = MapTemplate(
            w, h,
            [
                [MapPointStatus.EMPTY if x == 2 and y == 3 else MapPointStatus.PLAYER for y in range(h)]
                for x in range(w)
            ],
            {})

        self.assertEqual(mt.points[2][3], MapPointStatus.EMPTY)

    def test_to_model(self):
        w = MapTemplate.MIN_WIDTH + 1
        h = MapTemplate.MIN_HEIGHT + 3

        mdl = MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(h)] for _ in range(w)], {}).to_model()

        pt_status = [
            [
                MapPointModel(Status=MapPointStatus.PLAYER, Coord=MapCoordinateModel(X=x, Y=y))
                for y in range(h)
            ] for x in range(w)
        ]

        self.assertEqual(mdl, MapModel(Width=w, Height=h, Points=pt_status, Resources={}))

    def test_to_model_point_orientation(self):
        w = MapTemplate.MIN_WIDTH + 1
        h = MapTemplate.MIN_HEIGHT + 3

        mdl = MapTemplate(
            w, h,
            [
                [MapPointStatus.EMPTY if x == 2 and y == 3 else MapPointStatus.PLAYER for y in range(h)]
                for x in range(w)
            ],
            {}).to_model()

        pt_status = [
            [
                MapPointModel(
                    Status=MapPointStatus.EMPTY if x == 2 and y == 3 else MapPointStatus.PLAYER,
                    Coord=MapCoordinateModel(X=x, Y=y)
                )
                for y in range(h)
            ] for x in range(w)
        ]

        self.assertEqual(mdl, MapModel(Width=w, Height=h, Points=pt_status, Resources={}))
        self.assertEqual(mdl.points[2][3].status, MapPointStatus.EMPTY)
        self.assertEqual(mdl.points[2][3].coord, MapCoordinateModel(X=2, Y=3))

    def test_insuf_width(self):
        w = MapTemplate.MIN_WIDTH - 1
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(MapDimensionTooSmallError):
            MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(h)] for _ in range(w)], {})

    def test_insuf_height(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT - 1

        with self.assertRaises(MapDimensionTooSmallError):
            MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(h)] for _ in range(w)], {})

    def test_insuf_points(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(MapTooFewPointsError):
            MapTemplate(w, h,
                        [[MapPointStatus.EMPTY for _ in range(h)] for _ in range(w - 2)]
                        + [
                            [MapPointStatus.UNAVAILABLE for _ in range(w)]
                            + [MapPointStatus.PLAYER for _ in range(w)]
                        ],
                        {})

    def test_unspawnable(self):
        w = MapTemplate.MIN_WIDTH + 1
        h = MapTemplate.MIN_HEIGHT + 1

        with self.assertRaises(MapPointUnspawnableError):
            MapTemplate(w, h,
                        [[MapPointStatus.PLAYER for _ in range(h)] for _ in range(w - 1)]
                        + [[MapPointStatus.UNAVAILABLE for _ in range(h)]],
                        {MapPointResource.CHEST: [MapCoordinateModel(X=w - 1, Y=h - 1)]})

    def test_res_out_of_map(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(SpawnPointOutOfMapError):
            MapTemplate(w, h, [[MapPointStatus.PLAYER for _ in range(h)] for _ in range(w)],
                        {MapPointResource.CHEST: [MapCoordinateModel(X=w, Y=h)]})

    def test_no_player(self):
        w = MapTemplate.MIN_WIDTH
        h = MapTemplate.MIN_HEIGHT

        with self.assertRaises(NoPlayerSpawnPointError):
            MapTemplate(w, h, [[MapPointStatus.EMPTY for _ in range(h)] for _ in range(w)],
                        {MapPointResource.CHEST: [MapCoordinateModel(X=w, Y=h)]})

    def test_parse_file(self):
        mt = MapTemplate.load_from_file("tests/game_pkchess/res/map/map")

        self.assertEqual(mt.width, 9)
        self.assertEqual(mt.height, 9)
        self.assertEqual(
            mt.points,
            [
                [MapPointStatus.EMPTY] * 5
                + [MapPointStatus.PLAYER]
                + [MapPointStatus.CHEST]
                + [MapPointStatus.MONSTER]
                + [MapPointStatus.FIELD_BOSS]
            ] * 9
        )
        self.assertEqual(
            mt.resources,
            {
                MapPointResource.CHEST: [MapCoordinateModel(X=3, Y=y) for y in range(1, 4)],
                MapPointResource.MONSTER: [MapCoordinateModel(X=4, Y=y) for y in range(1, 4)],
                MapPointResource.FIELD_BOSS: [MapCoordinateModel(X=5, Y=y) for y in range(1, 4)]
            }
        )

    def test_parse_file_unspawnable(self):
        with self.assertRaises(MapPointUnspawnableError):
            MapTemplate.load_from_file("tests/game_pkchess/res/map/map_unspawnable")

    def test_parse_file_res_out_of_map(self):
        with self.assertRaises(SpawnPointOutOfMapError):
            MapTemplate.load_from_file("tests/game_pkchess/res/map/map_outofmap")

    def test_parse_file_unknown_resource(self):
        with self.assertRaises(UnknownResourceTypeError):
            MapTemplate.load_from_file("tests/game_pkchess/res/map/map_resource")

    def test_parse_file_no_player(self):
        with self.assertRaises(NoPlayerSpawnPointError):
            MapTemplate.load_from_file("tests/game_pkchess/res/map/map_noplayer")


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
            ("obj", "Obj"): (None, Character())
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
            ("pt", "Points"): [
                [MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=0)),
                 MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=1))],
                [MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=0)),
                 MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=1))]
            ],
            ("res", "Resources"): {
                MapPointResource.CHEST: [MapCoordinateModel(X=0, Y=0), MapCoordinateModel(X=1, Y=1)]
            }
        }
