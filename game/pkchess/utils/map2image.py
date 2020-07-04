"""
This module contains the utility to convert the map into an image.

Any 3-tuple or 4-tuple seen in this module is usually a color, representing RGB or RGBA.
"""
from typing import Union, Tuple, Dict, Optional, List

from PIL import Image, ImageDraw
from bson import ObjectId

from game.pkchess.exception import PlayerIconNotExistsError
from game.pkchess.flags import MapPointStatus
from game.pkchess.map import MapTemplate, MapModel, Map, MapPoint, MapCoordinate
from .image import replace_color

__all__ = ["MapImageGenerator", "MapPointUnitDrawer",
           "ICON_PLAYER_COLORS", "ICON_PLAYER_DEFAULT_COLOR", "ICON_PLAYER_DEFAULT"]


def _generate_character_icons(colors: List[Tuple[int, int, int]]) -> (List[Image.Image], List[Image.Image]):
    """
    Generate the icons of the characters by providing the colors to be used.

    :param colors: colors to be used for the image
    :return: a tuple which the first element is the player icon and the second is current player icon

    .. note::
        Copied and modified from https://stackoverflow.com/a/3753428/11571888
    """
    player_icons = [
        replace_color("game/pkchess/res/mapobj/player.png", ICON_PLAYER_DEFAULT_COLOR, color)
        for color in colors
    ]
    player_icons_current = [
        replace_color("game/pkchess/res/mapobj/player_current.png", ICON_PLAYER_DEFAULT_COLOR, color)
        for color in colors
    ]

    return player_icons, player_icons_current


ICON_PLAYER_DEFAULT = Image.open("game/pkchess/res/mapobj/player.png")
ICON_PLAYER_DEFAULT_COLOR = (128, 128, 128)
ICON_PLAYER_COLORS = [
    (0, 38, 255),  # 1P - Blue
    (224, 163, 0),  # 2P - Golden Yellow
    (255, 106, 0),  # 3P - Orange
    (76, 255, 0)  # 4P - Lighter Green
]
ICON_PLAYER_IDX, ICON_PLAYER_IDX_CURRENT = _generate_character_icons(ICON_PLAYER_COLORS)
ICON_CHEST = Image.open("game/pkchess/res/mapobj/chest.png")
ICON_MONSTER = Image.open("game/pkchess/res/mapobj/monster.png")
ICON_BOSS = Image.open("game/pkchess/res/mapobj/boss.png")


class MapPointUnitDrawer:
    SIZE = 50

    PADDING = 2

    HP_AREA_HEIGHT = 3
    HP_BAR_COLOR = [
        (0, 255, 0),  # >60% - Green
        (255, 255, 0),  # >30% & <= 60% - Yellow
        (255, 0, 0)  # <= 30% - Red
    ]

    OUTLINE_COLOR = (50, 50, 50)
    OUTLINE_WIDTH = 2

    @classmethod
    def _get_hp_fill_color(cls, map_point: MapPoint):
        hp_ratio = map_point.obj.hp_ratio

        if hp_ratio < 0.3:
            return cls.HP_BAR_COLOR[2]

        if 0.3 < hp_ratio <= 0.6:
            return cls.HP_BAR_COLOR[1]

        return cls.HP_BAR_COLOR[0]

    @classmethod
    def draw_hp_bar(cls, img: Image.Image, map_point: MapPoint):
        bar_lt_x = map_point.coord.X * cls.SIZE + cls.PADDING * 2
        bar_lt_y = map_point.coord.Y * cls.SIZE + cls.PADDING * 2
        bar_rb_x = (map_point.coord.X + 1) * cls.SIZE - cls.PADDING * 2
        bar_rb_y = bar_lt_y + cls.HP_AREA_HEIGHT

        ImageDraw.Draw(img).rectangle([(bar_lt_x, bar_lt_y), (bar_rb_x, bar_rb_y)],
                                      fill=cls._get_hp_fill_color(map_point))

    @classmethod
    def draw_unavailable(cls, img: Image.Image, map_point: MapPoint):
        ImageDraw.Draw(img).rectangle(cls.get_coord_on_image(map_point.coord), fill=(0, 0, 0))

    @classmethod
    def draw_empty(cls, img: Image.Image, map_point: MapPoint):
        ImageDraw.Draw(img).rectangle(cls.get_coord_on_image(map_point.coord), outline=(50, 50, 50), width=2)

    @classmethod
    def draw_chest(cls, img: Image.Image, map_point: MapPoint):
        img.paste(ICON_CHEST, cls.get_coord_on_image(map_point.coord, with_padding=False)[0])

    @classmethod
    def draw_monster(cls, img: Image.Image, map_point: MapPoint):
        img.paste(ICON_MONSTER, cls.get_coord_on_image(map_point.coord, with_padding=False)[0])

        if map_point.obj is not None:
            cls.draw_hp_bar(img, map_point)

    @classmethod
    def draw_field_boss(cls, img: Image.Image, map_point: MapPoint):
        img.paste(ICON_BOSS, cls.get_coord_on_image(map_point.coord, with_padding=False)[0])

        if map_point.obj is not None:
            cls.draw_hp_bar(img, map_point)

    @classmethod
    def draw_player(cls, img: Image.Image, map_point: MapPoint, player_location: Dict[ObjectId, MapCoordinate],
                    player_idx_dict: Dict[ObjectId, int] = None, current_idx: Optional[int] = None):
        # Draw default icon if no index information is given
        if player_idx_dict is None or current_idx is None:
            img.paste(ICON_PLAYER_DEFAULT, cls.get_coord_on_image(map_point.coord, with_padding=False)[0])
            return

        # Try to get the player index, draw default icon if no match with ``player_idx_dict``
        player_idx = None
        for player_oid, player_coord in player_location.items():
            if map_point.coord == player_coord and player_oid in player_idx_dict:
                player_idx = player_idx_dict[player_oid]
                break

        if player_idx is None:
            img.paste(ICON_PLAYER_DEFAULT, cls.get_coord_on_image(map_point.coord, with_padding=False)[0])
            return

        # Raise an error if the icon color is not designed yet
        if player_idx >= len(ICON_PLAYER_IDX):
            raise PlayerIconNotExistsError()

        if current_idx == player_idx:
            # Draw the current icon if the player index is the current one
            img.paste(ICON_PLAYER_IDX_CURRENT[player_idx],
                      cls.get_coord_on_image(map_point.coord, with_padding=False)[0])
        else:
            # Draw normal player icon with index
            img.paste(ICON_PLAYER_IDX[player_idx],
                      cls.get_coord_on_image(map_point.coord, with_padding=False)[0])

        if map_point.obj is not None:
            cls.draw_hp_bar(img, map_point)

    @classmethod
    def get_coord_on_image(cls, point_coord: MapCoordinate, *, with_padding: bool = True) \
            -> [Tuple[int, int], Tuple[int, int]]:
        size = cls.SIZE
        padding = cls.PADDING if with_padding else 0

        return [
            (point_coord.X * size + padding, point_coord.Y * size + padding),
            ((point_coord.X + 1) * size - padding, (point_coord.Y + 1) * size - padding)
        ]


class MapImageGenerator:
    @staticmethod
    def generate_image(game_map: Union[Map, MapTemplate, MapModel], *,
                       player_idx_dict: Optional[Dict[ObjectId, int]] = None,
                       current_idx: Optional[int] = None) \
            -> Image.Image:
        """
        Generate the image of the map using Pillow.

        Both ``player_idx_dict`` and ``current_index`` should all be given or not given at the same time.

        The key of ``player_idx_dict`` is the OID of the player and
        its value is the turn index of the corresponding player.

        The map will use the default player icon if ``player_idx_dict`` is ``None``.
        Otherwise, the player icon will be rendered according to their index.

        :param game_map: game map to be generated an image
        :param player_idx_dict: player idx correspondence dict
        :param current_idx: current player index
        :return: Pillow image object
        """
        if isinstance(game_map, (MapTemplate, MapModel)):
            game_map = game_map.to_map()

        # Create a blank image
        image = Image.new(
            "RGBA",
            (game_map.width * MapPointUnitDrawer.SIZE, game_map.height * MapPointUnitDrawer.SIZE),
            (255, 255, 255, 0)
        )

        for map_point in game_map.points_flattened:
            if map_point.status == MapPointStatus.UNAVAILABLE:
                MapPointUnitDrawer.draw_unavailable(image, map_point)
            elif map_point.status == MapPointStatus.EMPTY:
                MapPointUnitDrawer.draw_empty(image, map_point)
            elif map_point.status == MapPointStatus.PLAYER:
                MapPointUnitDrawer.draw_player(
                    image, map_point, game_map.player_location, player_idx_dict, current_idx)
            elif map_point.status == MapPointStatus.CHEST:
                MapPointUnitDrawer.draw_chest(image, map_point)
            elif map_point.status == MapPointStatus.MONSTER:
                MapPointUnitDrawer.draw_monster(image, map_point)
            elif map_point.status == MapPointStatus.FIELD_BOSS:
                MapPointUnitDrawer.draw_field_boss(image, map_point)

        return image
