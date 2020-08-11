from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.exception import GameNotReadyError
from game.pkchess.res import character_templates, get_map_template
from game.pkchess.game import PendingGame, PlayerEntry, RunningGame
from tests.base import TestCase

__all__ = ["TestPendingGame"]


class TestPendingGame(TestCase):
    CHANNEL_OID = ObjectId()

    PLAYER_OID_1 = ObjectId()
    PLAYER_OID_2 = ObjectId()

    def test_ready_insuf_players(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertFalse(game.ready)

    def test_ready_not_all_ready(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"])),
                self.PLAYER_OID_2: PlayerEntry(self.PLAYER_OID_2, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertFalse(game.ready)

    def test_ready_map_not_decided(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"])),
                self.PLAYER_OID_2: PlayerEntry(self.PLAYER_OID_2, Character(character_templates["nearnox"]), True),
            }
        )

        self.assertFalse(game.ready)

    def test_ready(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True),
                self.PLAYER_OID_2: PlayerEntry(self.PLAYER_OID_2, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertTrue(game.ready)

    def test_add_player_exists(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertFalse(game.add_player(self.PLAYER_OID_1, Character(character_templates["nearnox"])))
        self.assertTrue(self.PLAYER_OID_1 in game.players)

    def test_add_player(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertTrue(game.add_player(self.PLAYER_OID_2, Character(character_templates["nearnox"])))
        self.assertTrue(self.PLAYER_OID_2 in game.players)

    def test_player_ready_not_exists(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertFalse(game.player_ready(self.PLAYER_OID_2))
        self.assertTrue(self.PLAYER_OID_2 not in game.players)

    def test_player_ready_update_to_same(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertTrue(game.player_ready(self.PLAYER_OID_1))
        self.assertTrue(game.players[self.PLAYER_OID_1].ready)

    def test_player_ready_specified(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True),
            },
            get_map_template("map01")
        )

        self.assertTrue(game.player_ready(self.PLAYER_OID_1, ready=False))
        self.assertFalse(game.players[self.PLAYER_OID_1].ready)

    def test_player_ready(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"])),
            },
            get_map_template("map01")
        )

        self.assertTrue(game.player_ready(self.PLAYER_OID_1))
        self.assertTrue(game.players[self.PLAYER_OID_1].ready)

    def test_start_game_not_ready(self):
        game = PendingGame(
            self.CHANNEL_OID,
            {
                self.PLAYER_OID_1: PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"])),
                self.PLAYER_OID_2: PlayerEntry(self.PLAYER_OID_2, Character(character_templates["nearnox"])),
            },
            get_map_template("map01")
        )

        with self.assertRaises(GameNotReadyError):
            game.start_game()

    def test_start_game(self):
        entry_1 = PlayerEntry(self.PLAYER_OID_1, Character(character_templates["nearnox"]), True)
        entry_2 = PlayerEntry(self.PLAYER_OID_2, Character(character_templates["nearnox"]), True)

        game = PendingGame(
            self.CHANNEL_OID,
            {self.PLAYER_OID_1: entry_1, self.PLAYER_OID_2: entry_2},
            get_map_template("map01")
        )

        running_game = game.start_game()

        self.assertIsInstance(running_game, RunningGame)
        self.assertEqual(
            set(running_game.players),
            {entry_1, entry_2}
        )
        self.assertEqual(running_game.current_idx, 0)
        self.assertEqual(running_game.map.template, get_map_template("map01"))
