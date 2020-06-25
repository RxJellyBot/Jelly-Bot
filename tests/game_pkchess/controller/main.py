from typing import List, Union, Type

from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.controller import GameController
from game.pkchess.flags import (
    GameCreationResult, GameMapSetResult, GameReadyResult, GameStartResult, PlayerActionResult,
    MapPointStatus, MapPointResource
)
from game.pkchess.game import PlayerEntry, RunningGame
from game.pkchess.map import MapTemplate, MapCoordinate
from game.pkchess.res import get_map_template
from game.pkchess.utils.character import get_character_template
from mixin import ClearableMixin
from tests.base import TestCase

__all__ = ["TestGameController"]


class TestGameController(TestCase):
    CHANNEL_OID = ObjectId()

    PLAYER_OID_1 = ObjectId()
    PLAYER_OID_2 = ObjectId()

    PLAYER_ENTRY_1 = PlayerEntry(PLAYER_OID_1, Character(get_character_template("Nearnox")), True)
    PLAYER_ENTRY_2 = PlayerEntry(PLAYER_OID_2, Character(get_character_template("Nearnox")), True)

    TEMPLATE = MapTemplate(
        2, 3,
        [
            [
                MapPointStatus.EMPTY,
                MapPointStatus.CHEST,
                MapPointStatus.PLAYER
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

    @staticmethod
    def obj_to_clear() -> List[Union[Type[ClearableMixin], ClearableMixin]]:
        return [GameController]

    def _create_game(self, *, ready: bool = True, map_decided: bool = True):
        self.assertEqual(
            GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox"),
            GameCreationResult.O_CREATED
        )
        self.assertEqual(
            GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_2, "Nearnox"),
            GameCreationResult.O_JOINED
        )

        if ready:
            self.assertEqual(
                GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_1),
                GameReadyResult.O_UPDATED
            )
            self.assertEqual(
                GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_2),
                GameReadyResult.O_UPDATED
            )

        if map_decided:
            self.assertEqual(
                GameController.pending_game_set_map(self.CHANNEL_OID, "map01"),
                GameMapSetResult.O_SET
            )

    def _start_game(self):
        GameController.set_running_game(
            self.CHANNEL_OID,
            RunningGame(
                self.CHANNEL_OID, self.TEMPLATE.to_map(
                    player_location={self.PLAYER_OID_1: MapCoordinate(1, 1),
                                     self.PLAYER_OID_2: MapCoordinate(0, 2)}
                ),
                [self.PLAYER_ENTRY_1, self.PLAYER_ENTRY_2]
            )
        )

    def test_join_pending_existed(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")
        result = GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_2, "Nearnox")

        self.assertEqual(result, GameCreationResult.O_JOINED)
        game = GameController.get_pending_game(self.CHANNEL_OID)
        self.assertIsNotNone(game)
        self.assertEqual(game.channel_oid, self.CHANNEL_OID)
        self.assertEqual(len(game.players), 2)
        plyr1 = game.players[self.PLAYER_OID_1]
        self.assertEqual(plyr1.player_oid, self.PLAYER_OID_1)
        self.assertEqual(plyr1.character, Character(get_character_template("Nearnox")))
        self.assertEqual(plyr1.ready, False)
        plyr2 = game.players[self.PLAYER_OID_2]
        self.assertEqual(plyr2.player_oid, self.PLAYER_OID_2)
        self.assertEqual(plyr2.character, Character(get_character_template("Nearnox")))
        self.assertEqual(plyr2.ready, False)

    def test_join_pending_new(self):
        result = GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")

        self.assertEqual(result, GameCreationResult.O_CREATED)
        game = GameController.get_pending_game(self.CHANNEL_OID)
        self.assertIsNotNone(game)
        self.assertEqual(game.channel_oid, self.CHANNEL_OID)
        self.assertEqual(len(game.players), 1)
        self.assertTrue(self.PLAYER_OID_2 not in game.players)
        plyr1 = game.players[self.PLAYER_OID_1]
        self.assertEqual(plyr1.player_oid, self.PLAYER_OID_1)
        self.assertEqual(plyr1.character, Character(get_character_template("Nearnox")))
        self.assertEqual(plyr1.ready, False)

    def test_join_pending_chara_name_case_insensitive(self):
        result = GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "nEaRnOx")

        self.assertEqual(result, GameCreationResult.O_CREATED)
        game = GameController.get_pending_game(self.CHANNEL_OID)
        self.assertIsNotNone(game)
        self.assertEqual(game.channel_oid, self.CHANNEL_OID)
        self.assertEqual(len(game.players), 1)
        self.assertTrue(self.PLAYER_OID_2 not in game.players)
        plyr1 = game.players[self.PLAYER_OID_1]
        self.assertEqual(plyr1.player_oid, self.PLAYER_OID_1)
        self.assertEqual(plyr1.character, Character(get_character_template("Nearnox")))
        self.assertEqual(plyr1.ready, False)

    def test_join_pending_already_joined(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")
        result = GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")

        self.assertEqual(result, GameCreationResult.X_ALREADY_JOINED)
        game = GameController.get_pending_game(self.CHANNEL_OID)
        self.assertIsNotNone(game)
        self.assertEqual(game.channel_oid, self.CHANNEL_OID)
        self.assertEqual(len(game.players), 1)
        self.assertTrue(self.PLAYER_OID_2 not in game.players)
        plyr1 = game.players[self.PLAYER_OID_1]
        self.assertEqual(plyr1.player_oid, self.PLAYER_OID_1)
        self.assertEqual(plyr1.character, Character(get_character_template("Nearnox")))
        self.assertEqual(plyr1.ready, False)

    def test_join_pending_no_character_new(self):
        result = GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "ABCDEF")

        self.assertEqual(result, GameCreationResult.X_CHARACTER_NOT_EXIST)
        game = GameController.get_pending_game(self.CHANNEL_OID)
        self.assertIsNone(game)

    def test_join_pending_no_character_existed(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_2, "Nearnox")
        result = GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "ABCDEF")

        self.assertEqual(result, GameCreationResult.X_CHARACTER_NOT_EXIST)
        game = GameController.get_pending_game(self.CHANNEL_OID)
        self.assertIsNotNone(game)
        self.assertEqual(len(game.players), 1)
        self.assertTrue(self.PLAYER_OID_1 not in game.players)
        plyr1 = game.players[self.PLAYER_OID_2]
        self.assertEqual(plyr1.player_oid, self.PLAYER_OID_2)
        self.assertEqual(plyr1.character, Character(get_character_template("Nearnox")))
        self.assertEqual(plyr1.ready, False)

    def test_set_pending_map(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")

        self.assertEqual(GameMapSetResult.O_SET, GameController.pending_game_set_map(self.CHANNEL_OID, "map01"))
        self.assertEqual(GameController.get_pending_game(self.CHANNEL_OID).map_template, get_map_template("map01"))

    def test_set_pending_map_no_game(self):
        self.assertEqual(
            GameMapSetResult.X_GAME_NOT_FOUND,
            GameController.pending_game_set_map(self.CHANNEL_OID, "map01")
        )
        self.assertIsNone(GameController.get_pending_game(self.CHANNEL_OID))

    def test_set_pending_map_no_map(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")

        self.assertEqual(
            GameMapSetResult.X_TEMPLATE_NOT_FOUND,
            GameController.pending_game_set_map(self.CHANNEL_OID, "ABCDEF")
        )
        self.assertIsNone(GameController.get_pending_game(self.CHANNEL_OID).map_template)

    def test_set_ready(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")

        self.assertFalse(GameController.get_pending_game(self.CHANNEL_OID).players[self.PLAYER_OID_1].ready)
        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_1),
            GameReadyResult.O_UPDATED
        )
        self.assertTrue(GameController.get_pending_game(self.CHANNEL_OID).players[self.PLAYER_OID_1].ready)

    def test_set_ready_game_not_found(self):
        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_1),
            GameReadyResult.X_GAME_NOT_FOUND
        )
        self.assertIsNone(GameController.get_pending_game(self.CHANNEL_OID))

    def test_set_ready_game_unready(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")

        self.assertFalse(GameController.get_pending_game(self.CHANNEL_OID).players[self.PLAYER_OID_1].ready)
        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_1),
            GameReadyResult.O_UPDATED
        )
        self.assertTrue(GameController.get_pending_game(self.CHANNEL_OID).players[self.PLAYER_OID_1].ready)
        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_1, ready=False),
            GameReadyResult.O_UPDATED
        )
        self.assertFalse(GameController.get_pending_game(self.CHANNEL_OID).players[self.PLAYER_OID_1].ready)
        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_1, ready=False),
            GameReadyResult.O_UPDATED
        )
        self.assertFalse(GameController.get_pending_game(self.CHANNEL_OID).players[self.PLAYER_OID_1].ready)

    def test_set_ready_player_not_found(self):
        GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox")

        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_2),
            GameReadyResult.X_PLAYER_NOT_FOUND
        )
        self.assertTrue(self.PLAYER_OID_2 not in GameController.get_pending_game(self.CHANNEL_OID).players)

    def test_start_game_not_ready(self):
        self._create_game(ready=False)

        self.assertEqual(GameController.start_game(self.CHANNEL_OID), GameStartResult.X_GAME_NOT_READY)

    def test_start_game_not_exists(self):
        self.assertEqual(GameController.start_game(self.CHANNEL_OID), GameStartResult.X_GAME_NOT_FOUND)

    def test_start_game_have_one_started(self):
        self._create_game()
        self.assertEqual(GameController.start_game(self.CHANNEL_OID), GameStartResult.O_STARTED)
        self._create_game()

        self.assertEqual(GameController.start_game(self.CHANNEL_OID), GameStartResult.X_GAME_EXISTED)

    def test_start_game_map_not_specified(self):
        self._create_game(map_decided=False)
        self.assertEqual(GameController.start_game(self.CHANNEL_OID), GameStartResult.X_GAME_NOT_READY)

    def test_start_game(self):
        self._create_game()
        self.assertEqual(GameController.start_game(self.CHANNEL_OID), GameStartResult.O_STARTED)

        game = GameController.get_running_game(self.CHANNEL_OID)
        self.assertIsNotNone(game)
        self.assertEqual(game.channel_oid, self.CHANNEL_OID)
        self.assertEqual(
            set(game.players),
            {
                PlayerEntry(self.PLAYER_OID_1, Character(get_character_template("Nearnox")), True),
                PlayerEntry(self.PLAYER_OID_2, Character(get_character_template("Nearnox")), True)
            }
        )
        self.assertEqual(game.current_idx, 0)
        self.assertEqual(len(game.map.player_location), 2)
        self.assertEqual(sum(map(lambda pt: pt.status == MapPointStatus.PLAYER, game.map.points_flattened)), 2)

    def test_player_move_pending(self):
        self._create_game()

        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, 0, 1),
            PlayerActionResult.X_GAME_NOT_STARTED
        )

    def test_player_move_game_not_found(self):
        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, 0, 1),
            PlayerActionResult.X_GAME_NOT_FOUND
        )

    def test_player_move_already_moved(self):
        self._start_game()

        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, 0, 1),
            PlayerActionResult.O_ACTED
        )
        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, 0, -1),
            PlayerActionResult.X_ALREADY_MOVED
        )

    def test_player_move_player_not_in_game(self):
        self._start_game()

        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, ObjectId(), 0, 1),
            PlayerActionResult.X_PLAYER_NOT_EXISTS
        )

    def test_player_move_player_not_current(self):
        self._start_game()

        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_2, 0, 1),
            PlayerActionResult.X_PLAYER_NOT_CURRENT
        )

    def test_player_move_too_many_moves(self):
        self._start_game()

        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, 99, 99),
            PlayerActionResult.X_TOO_MANY_MOVES
        )

    def test_player_move_destination_not_empty(self):
        self._start_game()

        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, -1, 0),
            PlayerActionResult.X_DESTINATION_NOT_EMPTY
        )

    def test_player_move_out_of_map(self):
        self._start_game()

        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, -2, 0),
            PlayerActionResult.X_DESTINATION_OUT_OF_MAP
        )
        self.assertEqual(
            GameController.player_move(self.CHANNEL_OID, self.PLAYER_OID_1, 2, 0),
            PlayerActionResult.X_DESTINATION_OUT_OF_MAP
        )
