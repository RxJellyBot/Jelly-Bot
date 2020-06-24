from typing import List, Union, Type

from bson import ObjectId

from game.pkchess.controller import GameController
from game.pkchess.flags import GameCreationResult
from mixin import ClearableMixin
from tests.base import TestCase

__all__ = ["TestGameController"]


class TestGameController(TestCase):
    CHANNEL_OID = ObjectId()

    PLAYER_OID_1 = ObjectId()
    PLAYER_OID_2 = ObjectId()

    @staticmethod
    def obj_to_clear() -> List[Union[Type[ClearableMixin], ClearableMixin]]:
        return [GameController]

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
        self.assertEqual(plyr1.character_name, "Nearnox")
        self.assertEqual(plyr1.ready, False)
        plyr2 = game.players[self.PLAYER_OID_2]
        self.assertEqual(plyr2.player_oid, self.PLAYER_OID_2)
        self.assertEqual(plyr2.character_name, "Nearnox")
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
        self.assertEqual(plyr1.character_name, "Nearnox")
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
        self.assertEqual(plyr1.character_name, "Nearnox")
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
        self.assertEqual(plyr1.character_name, "Nearnox")
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
        self.assertEqual(plyr1.character_name, "Nearnox")
        self.assertEqual(plyr1.ready, False)
