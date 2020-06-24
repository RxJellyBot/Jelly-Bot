from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.map import Map, MapPoint, MapCoordinate, MapModel, MapPointModel, MapCoordinateModel, MapTemplate
from game.pkchess.utils.map2image import MapImageGenerator, MapPointUnitDrawer
from tests.base import TestCase

__all__ = ["TestMap2ImageGenerator"]


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
                }
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
                }
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
