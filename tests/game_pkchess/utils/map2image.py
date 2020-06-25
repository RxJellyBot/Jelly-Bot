from PIL import Image
from bson import ObjectId

from game.pkchess.exception import PlayerIconNotExistsError
from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.map import Map, MapPoint, MapCoordinate, MapModel, MapPointModel, MapCoordinateModel, MapTemplate
from game.pkchess.utils.image import replace_color
from game.pkchess.utils.map2image import (
    MapImageGenerator, MapPointUnitDrawer, ICON_PLAYER_COLORS, ICON_PLAYER_DEFAULT_COLOR, ICON_PLAYER_DEFAULT
)
from game.pkchess.res import get_map_template
from tests.base import TestCase, TestImageComparisonMixin

__all__ = ["TestMap2ImageGenerator", "TestMapImageDrawerCoord", "TestMapImageDrawer"]


class TestMap2ImageGenerator(TestCase):
    def test_generate_via_map(self):
        img = MapImageGenerator.generate_image(
            Map(
                2, 3,
                [
                    [
                        MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                        MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 1)),
                        MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
                    ],
                    [
                        MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                        MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 1)),
                        MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
                    ]
                ],
                {
                    MapPointResource.CHEST: [MapCoordinate(0, 1)]
                },
                get_map_template("map01")
            )
        )
        width, height = img.size

        self.assertIsNotNone(img)
        self.assertEqual(width, MapPointUnitDrawer.SIZE * 2)
        self.assertEqual(height, MapPointUnitDrawer.SIZE * 3)

    def test_generate_via_model(self):
        img = MapImageGenerator.generate_image(
            MapModel(
                Width=2, Height=3,
                Points=[
                    [
                        MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=0)),
                        MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=1)),
                        MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=0, Y=2))
                    ],
                    [
                        MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=0)),
                        MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=1)),
                        MapPointModel(Status=MapPointStatus.EMPTY, Coord=MapCoordinateModel(X=1, Y=2))
                    ]
                ],
                Resources={
                    MapPointResource.CHEST: [MapCoordinateModel(X=0, Y=1)]
                },
                TemplateName="map01", PlayerLocation={}
            )
        )

        width, height = img.size

        self.assertIsNotNone(img)
        self.assertEqual(width, MapPointUnitDrawer.SIZE * 2)
        self.assertEqual(height, MapPointUnitDrawer.SIZE * 3)

    def test_generate_via_template(self):
        img = MapImageGenerator.generate_image(
            MapTemplate(
                2, 3,
                [[MapPointStatus.EMPTY] * 3] * 2,
                {
                    MapPointResource.CHEST: [MapCoordinate(0, 1)]
                },
                bypass_map_chack=True
            )
        )
        width, height = img.size

        self.assertIsNotNone(img)
        self.assertEqual(width, MapPointUnitDrawer.SIZE * 2)
        self.assertEqual(height, MapPointUnitDrawer.SIZE * 3)


class TestMapImageDrawerCoord(TestCase):
    def setUpTestCase(self) -> None:
        self.assertEqual(MapPointUnitDrawer.SIZE, 50, "Recalculate the dimensions for each test cases.")
        self.assertEqual(MapPointUnitDrawer.PADDING, 2, "Recalculate the dimensions for each test cases.")

    def test_get_map_coord(self):
        self.assertEqual(MapPointUnitDrawer.get_coord_on_image(MapCoordinate(0, 0)), [(2, 2), (48, 48)])
        self.assertEqual(MapPointUnitDrawer.get_coord_on_image(MapCoordinate(0, 2)), [(2, 102), (48, 148)])
        self.assertEqual(MapPointUnitDrawer.get_coord_on_image(MapCoordinate(4, 0)), [(202, 2), (248, 48)])
        self.assertEqual(MapPointUnitDrawer.get_coord_on_image(MapCoordinate(1, 3)), [(52, 152), (98, 198)])

    def test_get_map_coord_without_padding(self):
        self.assertEqual(
            MapPointUnitDrawer.get_coord_on_image(MapCoordinate(0, 0), with_padding=False), [(0, 0), (50, 50)]
        )
        self.assertEqual(
            MapPointUnitDrawer.get_coord_on_image(MapCoordinate(0, 2), with_padding=False), [(0, 100), (50, 150)]
        )
        self.assertEqual(
            MapPointUnitDrawer.get_coord_on_image(MapCoordinate(4, 0), with_padding=False), [(200, 0), (250, 50)]
        )
        self.assertEqual(
            MapPointUnitDrawer.get_coord_on_image(MapCoordinate(1, 3), with_padding=False), [(50, 150), (100, 200)]
        )


class TestMapImageDrawer(TestImageComparisonMixin, TestCase):
    PLAYER_OID = ObjectId()

    def test_draw_player_no_idx_info(self):
        img = Image.new(
            "RGBA",
            (MapPointUnitDrawer.SIZE, MapPointUnitDrawer.SIZE),
            (255, 255, 255, 0)
        )

        MapPointUnitDrawer.draw_player(
            img, MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0)),
            {self.PLAYER_OID: MapCoordinate(0, 0)}
        )

        self.assertImageEqual(img, ICON_PLAYER_DEFAULT)

    def test_draw_player_is_current(self):
        img = Image.new(
            "RGBA",
            (MapPointUnitDrawer.SIZE, MapPointUnitDrawer.SIZE),
            (255, 255, 255, 0)
        )

        MapPointUnitDrawer.draw_player(
            img, MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0)),
            {self.PLAYER_OID: MapCoordinate(0, 0)},
            {self.PLAYER_OID: 1}, 1
        )

        color = ICON_PLAYER_COLORS[1]

        self.assertImageEqual(
            img,
            replace_color("game/pkchess/res/mapobj/player_current.png", ICON_PLAYER_DEFAULT_COLOR, color)
        )

    def test_draw_player_not_current(self):
        img = Image.new(
            "RGBA",
            (MapPointUnitDrawer.SIZE, MapPointUnitDrawer.SIZE),
            (255, 255, 255, 0)
        )

        MapPointUnitDrawer.draw_player(
            img, MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0)),
            {self.PLAYER_OID: MapCoordinate(0, 0)},
            {self.PLAYER_OID: 1}, 0
        )

        color = ICON_PLAYER_COLORS[1]

        self.assertImageEqual(
            img,
            replace_color("game/pkchess/res/mapobj/player.png", ICON_PLAYER_DEFAULT_COLOR, color)
        )

    def test_draw_player_idx_not_found(self):
        img = Image.new(
            "RGBA",
            (MapPointUnitDrawer.SIZE, MapPointUnitDrawer.SIZE),
            (255, 255, 255, 0)
        )

        MapPointUnitDrawer.draw_player(
            img, MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0)),
            {self.PLAYER_OID: MapCoordinate(0, 0)},
            {ObjectId(): 2}, 0
        )

        self.assertImageEqual(img, ICON_PLAYER_DEFAULT)

    def test_draw_player_no_icon(self):
        img = Image.new(
            "RGBA",
            (MapPointUnitDrawer.SIZE, MapPointUnitDrawer.SIZE),
            (255, 255, 255, 0)
        )

        with self.assertRaises(PlayerIconNotExistsError):
            MapPointUnitDrawer.draw_player(
                img, MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0)),
                {self.PLAYER_OID: MapCoordinate(0, 0)},
                {self.PLAYER_OID: 999},
                5
            )
