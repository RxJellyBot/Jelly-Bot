from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.exception import (
    CoordinateOutOfBoundError, MapTooManyPlayersError, MoveDestinationOutOfMapError, GamePlayerNotFoundError,
    CenterOutOfMapError, PathNotFoundError, PathSameDestinationError, PathEndOutOfMapError
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

        new = coord.apply_offset(1, 1)

        self.assertEqual(coord.X, 0)
        self.assertEqual(coord.Y, 3)
        self.assertEqual(new.X, 1)
        self.assertEqual(new.Y, 2)
        self.assertNotEqual(id(new), id(coord))

    def test_apply_offset_to_negative(self):
        coord = MapCoordinate(0, 3)

        with self.assertRaises(CoordinateOutOfBoundError):
            coord.apply_offset(-1, 1)

    def test_apply_offset_negative_val(self):
        coord = MapCoordinate(0, 3)

        new = coord.apply_offset(2, 3)

        self.assertEqual(coord.X, 0)
        self.assertEqual(coord.Y, 3)
        self.assertEqual(new.X, 2)
        self.assertEqual(new.Y, 0)
        self.assertNotEqual(id(new), id(coord))

    def test_distance(self):
        data = [
            (MapCoordinate(0, 3), MapCoordinate(1, 2), 2),
            (MapCoordinate(0, 0), MapCoordinate(0, 0), 0),
            (MapCoordinate(0, 0), MapCoordinate(0, 1), 1),
            (MapCoordinate(2, 3), MapCoordinate(4, 5), 4),
            (MapCoordinate(-7, -5), MapCoordinate(-8, -1), 5)
        ]

        for a, b, expected_distance in data:
            with self.subTest(point_a=a, point_b=b, expected_distance=expected_distance):
                self.assertEqual(a.distance(b), expected_distance)


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
                MapPointStatus.UNAVAILABLE,
                MapPointStatus.CHEST,
                MapPointStatus.EMPTY
            ],
            [
                MapPointStatus.EMPTY,
                MapPointStatus.PLAYER,
                MapPointStatus.EMPTY
            ]
        ],
        {
            MapPointResource.CHEST: [MapCoordinate(0, 1)]
        },
        bypass_map_chack=True
    )

    TEMPLATE_MOVE_2 = MapTemplate(
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
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        self.assertTrue(game_map.player_move(self.PLAYER_OID_1, 0, 1, 999))

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 0)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 0), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
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
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        self.assertTrue(game_map.player_move(self.PLAYER_OID_1, 0, -1, 999))

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 2)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 1)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 2), chara)
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_move_player_over_max_move(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE.to_map(
            players={self.PLAYER_OID_1: chara}
        )

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        with self.assertRaises(PathNotFoundError):
            game_map.player_move(self.PLAYER_OID_1, -1, -1, 1)

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_move_player_path_not_connected(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE_2.to_map(
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

        with self.assertRaises(PathNotFoundError):
            game_map.player_move(self.PLAYER_OID_1, -1, 1, 999)

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

    def test_move_player_out_of_map(self):
        chara = Character(get_character_template("Nearnox"))

        game_map = self.TEMPLATE_MOVE.to_map(
            players={self.PLAYER_OID_1: chara}
        )

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        with self.assertRaises(MoveDestinationOutOfMapError):
            game_map.player_move(self.PLAYER_OID_1, -2, -2, 999)
        with self.assertRaises(MoveDestinationOutOfMapError):
            game_map.player_move(self.PLAYER_OID_1, 2, 2, 999)

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
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
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        self.assertFalse(game_map.player_move(self.PLAYER_OID_1, -1, 0, 999))

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
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
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

        with self.assertRaises(GamePlayerNotFoundError):
            game_map.player_move(ObjectId(), 0, 0, 999)

        self.assertEqual(game_map.player_location, {self.PLAYER_OID_1: MapCoordinate(1, 1)})
        expected_points = [
            [
                MapPoint(MapPointStatus.UNAVAILABLE, MapCoordinate(0, 0)),
                MapPoint(MapPointStatus.CHEST, MapCoordinate(0, 1)),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(0, 2))
            ],
            [
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 0)),
                MapPoint(MapPointStatus.PLAYER, MapCoordinate(1, 1), chara),
                MapPoint(MapPointStatus.EMPTY, MapCoordinate(1, 2))
            ]
        ]
        for i in range(game_map.width):
            with self.subTest(x=i):
                self.assertEqual(game_map.points[i], expected_points[i])

    def test_get_points(self):
        game_map = self.TEMPLATE.to_map(player_location={self.PLAYER_OID_1: MapCoordinate(1, 1)})

        self.assertEqual(
            [pt.coord for pt in game_map.get_points(MapCoordinate(1, 1), [(0, 1), (-1, 0)])],
            [MapCoordinate(1, 0), MapCoordinate(0, 1)]
        )

    def test_get_points_center_out_of_map(self):
        game_map = self.TEMPLATE.to_map(player_location={self.PLAYER_OID_1: MapCoordinate(1, 1)})

        with self.assertRaises(CenterOutOfMapError):
            game_map.get_points(MapCoordinate(2, 2), [(0, 1), (-1, 0)])

    def test_get_points_offset_partial_out_of_map(self):
        game_map = self.TEMPLATE.to_map(player_location={self.PLAYER_OID_1: MapCoordinate(1, 1)})

        self.assertEqual(
            [pt.coord for pt in game_map.get_points(MapCoordinate(1, 1), [(0, 9), (-1, 0)])],
            [MapCoordinate(0, 1)]
        )

    def test_get_points_offset_out_of_map(self):
        game_map = self.TEMPLATE.to_map(player_location={self.PLAYER_OID_1: MapCoordinate(1, 1)})

        self.assertEqual(
            [pt.coord for pt in game_map.get_points(MapCoordinate(1, 1), [(0, 9), (-9, 0)])],
            []
        )

    def test_get_shortest_path(self):
        game_map = self.TEMPLATE_MOVE_2.to_map()

        self.assertEqual(
            game_map.get_shortest_path(MapCoordinate(1, 1), MapCoordinate(0, 2), 99),
            [MapCoordinate(1, 1), MapCoordinate(1, 2), MapCoordinate(0, 2)]
        )

    def test_get_shortest_path_destination_not_empty(self):
        game_map = self.TEMPLATE_MOVE.to_map()

        self.assertIsNone(game_map.get_shortest_path(MapCoordinate(1, 1), MapCoordinate(0, 0), 99))

    def test_get_shortest_path_path_not_found(self):
        game_map = self.TEMPLATE_MOVE_2.to_map()

        self.assertIsNone(game_map.get_shortest_path(MapCoordinate(1, 1), MapCoordinate(0, 0), 99))

    def test_get_shortest_path_over_length(self):
        game_map = self.TEMPLATE_MOVE_2.to_map()

        self.assertIsNone(game_map.get_shortest_path(MapCoordinate(1, 1), MapCoordinate(0, 2), 1))

    def test_get_shortest_path_exact_length(self):
        game_map = self.TEMPLATE_MOVE_2.to_map()

        self.assertEqual(
            game_map.get_shortest_path(MapCoordinate(1, 1), MapCoordinate(0, 2), 2),
            [MapCoordinate(1, 1), MapCoordinate(1, 2), MapCoordinate(0, 2)]
        )

    def test_get_shortest_path_same_destination(self):
        game_map = self.TEMPLATE_MOVE_2.to_map()

        with self.assertRaises(PathSameDestinationError):
            game_map.get_shortest_path(MapCoordinate(0, 0), MapCoordinate(0, 0), 99)

    def test_get_shortest_path_origin_out_of_map(self):
        game_map = self.TEMPLATE_MOVE_2.to_map()

        with self.assertRaises(PathEndOutOfMapError):
            game_map.get_shortest_path(MapCoordinate(3, 3), MapCoordinate(0, 0), 99)

    def test_get_shortest_path_destination_out_of_map(self):
        game_map = self.TEMPLATE_MOVE_2.to_map()

        with self.assertRaises(PathEndOutOfMapError):
            game_map.get_shortest_path(MapCoordinate(0, 0), MapCoordinate(3, 3), 99)

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
