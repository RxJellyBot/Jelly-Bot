from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.exception import (
    CoordinateOutOfBoundError, MapTooManyPlayersError, MoveDestinationOutOfMapError, GamePlayerNotFoundError
)
from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.map import MapTemplate, MapPoint, MapCoordinate
from game.pkchess.utils.character import get_character_template
from tests.base import TestCase

__all__ = ["TestMapCoordinate", "TestMap"]


class TestMapCoordinate(TestCase):
    CHANNEL_OID = ObjectId()

    PLAYER_OID_1 = ObjectId()
    PLAYER_OID_2 = ObjectId()

    def test_apply_offset(self):
        coord = MapCoordinate(0, 3)

        original, new = coord.apply_offset(1, 4)

        self.assertEqual(original.X, 0)
        self.assertEqual(original.Y, 3)
        self.assertEqual(id(original), id(coord))
        self.assertEqual(new.X, 1)
        self.assertEqual(new.Y, 7)
        self.assertNotEqual(id(new), id(coord))

    def test_apply_offset_to_negative(self):
        coord = MapCoordinate(0, 3)

        with self.assertRaises(CoordinateOutOfBoundError):
            coord.apply_offset(-1, 1)

    def test_apply_offset_negative_val(self):
        coord = MapCoordinate(0, 3)

        original, new = coord.apply_offset(2, -3)

        self.assertEqual(original.X, 0)
        self.assertEqual(original.Y, 3)
        self.assertEqual(id(original), id(coord))
        self.assertEqual(new.X, 2)
        self.assertEqual(new.Y, 0)
        self.assertNotEqual(id(new), id(coord))


class TestMap(TestCase):
    PLAYER_OID_1 = ObjectId()
    PLAYER_OID_2 = ObjectId()
    PLAYER_OID_3 = ObjectId()

    TEMPLATE = MapTemplate(
        2, 3,
        [
            [
                MapPointStatus.PLAYER,
                MapPointStatus.CHEST,
                MapPointStatus.EMPTY
            ],
            [
                MapPointStatus.UNAVAILABLE,
                MapPointStatus.PLAYER,
                MapPointStatus.PLAYER
            ]
        ],
        {
            MapPointResource.CHEST: [MapCoordinate(0, 1)]
        },
        bypass_map_chack=True
    )

    TEMPLATE_MOVE = MapTemplate(
        2, 3,
        [
            [
                MapPointStatus.EMPTY,
                MapPointStatus.CHEST,
                MapPointStatus.EMPTY
            ],
            [
                MapPointStatus.UNAVAILABLE,
                MapPointStatus.PLAYER,
                MapPointStatus.EMPTY
            ]
        ],
        {
            MapPointResource.CHEST: [MapCoordinate(0, 1)]
        },
        bypass_map_chack=True
    )

    def test_new_map_plyr_locn_given(self):
        game_map = self.TEMPLATE.to_map(player_location={self.PLAYER_OID_1: MapCoordinate(1, 1)})

        self.assertEqual(game_map.width, 2)
        self.assertEqual(game_map.height, 3)
        self.assertEqual(game_map.template, self.TEMPLATE)
        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        self.assertEqual(game_map.resources, {MapPointResource.CHEST: [MapCoordinate(0, 1)]})

        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_new_map_plyr_locn_given_on_template_empty(self):
        game_map = self.TEMPLATE.to_map(player_location={self.PLAYER_OID_1: MapCoordinate(0, 2)})

        self.assertEqual(game_map.width, 2)
        self.assertEqual(game_map.height, 3)
        self.assertEqual(game_map.template, self.TEMPLATE)
        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(0, 2)})
        self.assertEqual(game_map.resources, {MapPointResource.CHEST: [MapCoordinate(0, 1)]})

        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_new_map_plyr_locn_given_on_template_undeployable(self):
        game_map = self.TEMPLATE.to_map(player_location={self.PLAYER_OID_1: MapCoordinate(1, 0)})

        self.assertEqual(game_map.width, 2)
        self.assertEqual(game_map.height, 3)
        self.assertEqual(game_map.template, self.TEMPLATE)
        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 0)})
        self.assertEqual(game_map.resources, {MapPointResource.CHEST: [MapCoordinate(0, 1)]})

        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_new_map_no_players(self):
        game_map = self.TEMPLATE.to_map()

        self.assertEqual(game_map.width, 2)
        self.assertEqual(game_map.height, 3)
        self.assertEqual(game_map.template, self.TEMPLATE)
        self.assertEqual(game_map.player_location, {})
        self.assertEqual(game_map.resources, {MapPointResource.CHEST: [MapCoordinate(0, 1)]})

        expected_points = [
            [
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_new_map_players_gt_deployable(self):
        with self.assertRaises(MapTooManyPlayersError):
            self.TEMPLATE.to_map(
                players={
                    ObjectId(): Character(get_character_template("Nearnox")),
                    ObjectId(): Character(get_character_template("Nearnox")),
                    ObjectId(): Character(get_character_template("Nearnox")),
                    ObjectId(): Character(get_character_template("Nearnox"))
                }
            )

    def test_new_map_players_eq_deployable(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE.to_map(
            players={
                self.PLAYER_OID_1: chara,
                self.PLAYER_OID_2: chara,
                self.PLAYER_OID_3: chara
            }
        )

        self.assertEqual(game_map.width, 2)
        self.assertEqual(game_map.height, 3)
        self.assertEqual(game_map.template, self.TEMPLATE)
        self.assertEqual(len(game_map.player_location), 3)
        self.assertTrue(
            all(player_oid in (self.PLAYER_OID_1, self.PLAYER_OID_2, self.PLAYER_OID_3)
                for player_oid in game_map.player_location)
        )
        self.assertEqual(game_map.resources, {MapPointResource.CHEST: [MapCoordinate(0, 1)]})

        expected_points = [
            [
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0), chara),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 2), chara)
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_new_map_players_lt_deployable(self):
        game_map = self.TEMPLATE.to_map(
            players={
                self.PLAYER_OID_1: Character(get_character_template("Nearnox")),
                self.PLAYER_OID_2: Character(get_character_template("Nearnox"))
            }
        )

        self.assertEqual(game_map.width, 2)
        self.assertEqual(game_map.height, 3)
        self.assertEqual(game_map.template, self.TEMPLATE)
        self.assertEqual(len(game_map.player_location), 2)
        self.assertTrue(
            all(player_oid in (self.PLAYER_OID_1, self.PLAYER_OID_2) for player_oid in game_map.player_location)
        )
        self.assertEqual(game_map.resources, {MapPointResource.CHEST: [MapCoordinate(0, 1)]})
        self.assertEqual(sum(map(lambda pt: pt.status == MapPointStatus.PLAYER, game_map.points_flattened)), 2)
        self.assertEqual(sum(map(lambda pt: pt.status == MapPointStatus.CHEST, game_map.points_flattened)), 1)
        self.assertEqual(sum(map(lambda pt: pt.status == MapPointStatus.UNAVAILABLE, game_map.points_flattened)), 1)
        self.assertEqual(sum(map(lambda pt: pt.status == MapPointStatus.EMPTY, game_map.points_flattened)), 2)

    def test_move_player(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE.to_map(
            players={self.PLAYER_OID_1: chara}
        )

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        self.assertTrue(game_map.player_move(self.PLAYER_OID_1, 0, 1))

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 2)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 2), chara)
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_move_player_neg_val(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE.to_map(
            players={self.PLAYER_OID_1: chara}
        )

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        self.assertTrue(game_map.player_move(self.PLAYER_OID_1, -1, -1))

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(0, 0)})
        expected_points = [
            [
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0), chara),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_move_player_out_of_map(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE.to_map(
            players={self.PLAYER_OID_1: chara}
        )

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        with self.assertRaises(MoveDestinationOutOfMapError):
            game_map.player_move(self.PLAYER_OID_1, -2, -2)
        with self.assertRaises(MoveDestinationOutOfMapError):
            game_map.player_move(self.PLAYER_OID_1, 2, 2)

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_move_player_non_empty(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE.to_map(
            players={self.PLAYER_OID_1: chara}
        )

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        self.assertFalse(game_map.player_move(self.PLAYER_OID_1, -1, 0))

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_move_player_not_exists(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE.to_map(
            players={self.PLAYER_OID_1: chara}
        )

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        with self.assertRaises(GamePlayerNotFoundError):
            game_map.player_move(ObjectId(), 0, 0)

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_point_flattened(self):
        game_map = self.TEMPLATE.to_map()

        self.assertEqual(
            game_map.points_flattened,
            [
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2)),
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 2))
            ]
        )
