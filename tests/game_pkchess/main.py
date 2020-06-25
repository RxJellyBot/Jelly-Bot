from bson import ObjectId

from game.pkchess.controller import GameController
from game.pkchess.flags import (
    GameCreationResult, GameReadyResult, GameStartResult, GameMapSetResult, PlayerActionResult
)
from game.pkchess.utils.map2image import MapImageGenerator
from tests.base import TestCase


class TestMainGameFlow(TestCase):
    CHANNEL_OID = ObjectId()

    PLAYER_OID_1 = ObjectId()
    PLAYER_OID_2 = ObjectId()
    PLAYER_OID_3 = ObjectId()

    def test_expected_flow(self):
        self.assertEqual(
            GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_1, "Nearnox"),
            GameCreationResult.O_CREATED
        )
        self.assertEqual(
            GameController.join_pending_game(self.CHANNEL_OID, self.PLAYER_OID_2, "Nearnox"),
            GameCreationResult.O_JOINED
        )
        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_1),
            GameReadyResult.O_UPDATED
        )
        self.assertEqual(
            GameController.pending_game_ready(self.CHANNEL_OID, self.PLAYER_OID_2),
            GameReadyResult.O_UPDATED
        )
        self.assertEqual(
            GameController.pending_game_set_map(self.CHANNEL_OID, "map01"),
            GameMapSetResult.O_SET
        )
        self.assertEqual(
            GameController.start_game(self.CHANNEL_OID),
            GameStartResult.O_STARTED
        )
        self.assertEqual(
            GameController.player_move(
                self.CHANNEL_OID,
                GameController.get_running_game(self.CHANNEL_OID).current_player.player_oid,
                1, 0
            ),
            PlayerActionResult.O_ACTED
        )

        # View image
        running_game = GameController.get_running_game(self.CHANNEL_OID)

        idx_dict = {player_entry.player_oid: idx for idx, player_entry in enumerate(running_game.players)}

        MapImageGenerator.generate_image(
            running_game.map, player_idx_dict=idx_dict, current_idx=running_game.current_idx).show()
