"""
This module contains the utility to convert the map into an image.

Any 3-tuple or 4-tuple seen in this module is usually a color, representing RGB or RGBA.
"""
from typing import Union, Tuple

from PIL import Image, ImageDraw

from game.pkchess.flags import MapPointStatus
from game.pkchess.map import MapTemplate, MapModel, Map, MapPoint

__all__ = ["MapImageGenerator", "MapPointUnitDrawer"]

ICON_PLAYER = Image.open("game/pkchess/res/mapobj/player.png")
ICON_CHEST = Image.open("game/pkchess/res/mapobj/chest.png")
ICON_MONSTER = Image.open("game/pkchess/res/mapobj/monster.png")
ICON_BOSS = Image.open("game/pkchess/res/mapobj/boss.png")


class MapPointUnitDrawer:
    SIZE = 50

    PADDING = 2

    OUTLINE_COLOR = (50, 50, 50)
    OUTLINE_WIDTH = 2

    @classmethod
    def draw(cls, img: Image, map_point: MapPoint):
        # TEST: draw image

        # TODO: Render icon for player
        if map_point.status == MapPointStatus.UNAVAILABLE:
            ImageDraw.Draw(img).rectangle(cls.get_coord_on_image(map_point), fill=(0, 0, 0))
        elif map_point.status == MapPointStatus.EMPTY:
            ImageDraw.Draw(img).rectangle(cls.get_coord_on_image(map_point), outline=(50, 50, 50), width=2)
        elif map_point.status == MapPointStatus.PLAYER:
            img.paste(ICON_PLAYER, cls.get_coord_on_image(map_point, with_padding=False)[0])
        elif map_point.status == MapPointStatus.CHEST:
            img.paste(ICON_CHEST, cls.get_coord_on_image(map_point, with_padding=False)[0])
        elif map_point.status == MapPointStatus.MONSTER:
            img.paste(ICON_MONSTER, cls.get_coord_on_image(map_point, with_padding=False)[0])
        elif map_point.status == MapPointStatus.FIELD_BOSS:
            img.paste(ICON_BOSS, cls.get_coord_on_image(map_point, with_padding=False)[0])

    @classmethod
    def get_coord_on_image(cls, map_point: MapPoint, *, with_padding: bool = True) \
            -> [Tuple[int, int], Tuple[int, int]]:
        # TEST: get coord of image
        size = cls.SIZE
        padding = cls.PADDING if with_padding else 0

        return [
            (map_point.coord.X * size + padding, map_point.coord.Y * size + padding),
            ((map_point.coord.X + 1) * size - padding, (map_point.coord.Y + 1) * size - padding)
        ]


class MapImageGenerator:
    @staticmethod
    def generate_image(game_map: Union[Map, MapTemplate, MapModel]) -> Image:
        if isinstance(game_map, (MapTemplate, MapModel)):
            game_map = game_map.to_map()

        # Create a blank image
        image = Image.new(
            "RGBA",
            (game_map.width * MapPointUnitDrawer.SIZE, game_map.height * MapPointUnitDrawer.SIZE),
            (255, 255, 255, 0)
        )

        for map_point in game_map.points_flattened:
            MapPointUnitDrawer.draw(image, map_point)

        return image


if __name__ == '__main__':
    from game.pkchess.map import get_map_template

    MapImageGenerator.generate_image(get_map_template("map01")).save("D:/UserData/Downloads/img.png")
