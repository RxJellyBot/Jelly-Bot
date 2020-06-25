from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.exception import GameActionSubmittedError
from game.pkchess.flags import MapPointStatus, MapPointResource, PlayerAction
from game.pkchess.game import RunningGame, PlayerEntry
from game.pkchess.map import MapTemplate, MapCoordinate
from game.pkchess.utils.character import get_character_template
from tests.base import TestCase

__all__ = ["TestRunningGame"]


class TestRunningGame(TestCase):
    CHANNEL_OID = ObjectId()

    PLAYER_OID_1 = ObjectId()
    PLAYER_OID_2 = ObjectId()

    PLAYER_ENTRY_1 = PlayerEntry(PLAYER_OID_1, Character(get_character_template("Nearnox")), True)
    PLAYER_ENTRY_2 = PlayerEntry(PLAYER_OID_2, Character(get_character_template("Nearnox")), True)

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

    def setUpTestCase(self) -> None:
        self.game = RunningGame(
            self.CHANNEL_OID,
            self.TEMPLATE.to_map(
                players={self.PLAYER_OID_1: Character(get_character_template("Nearnox")),
                         self.PLAYER_OID_2: Character(get_character_template("Nearnox"))}),
            [self.PLAYER_ENTRY_1, self.PLAYER_ENTRY_2]
        )

    def test_get_current_player(self):
        self.assertEqual(self.game.current_idx, 0)
        self.assertEqual(self.game.current_player, self.PLAYER_ENTRY_1)

    def test_get_current_after_turns(self):
        expected = [
            (1, 0, self.PLAYER_ENTRY_1),
            (1, 1, self.PLAYER_ENTRY_2),
            (2, 0, self.PLAYER_ENTRY_1),
            (2, 1, self.PLAYER_ENTRY_2),
            (3, 0, self.PLAYER_ENTRY_1),
            (3, 1, self.PLAYER_ENTRY_2),
            (4, 0, self.PLAYER_ENTRY_1),
            (4, 1, self.PLAYER_ENTRY_2)
        ]

        for rounds, current_idx, current_player in expected:
            self.assertEqual(self.game.current_action_performed, {action: False for action in PlayerAction})
            self.assertEqual(self.game.current_rounds, rounds)
            self.assertEqual(self.game.current_idx, current_idx)
            self.assertEqual(self.game.current_player, current_player)

            self.game.current_player_finished()

    def test_player_action_done(self):
        self.assertFalse(self.game.is_current_action_done(PlayerAction.MOVE))
        self.game.record_action_done(PlayerAction.MOVE)
        self.assertTrue(self.game.is_current_action_done(PlayerAction.MOVE))
        with self.assertRaises(GameActionSubmittedError):
            self.game.record_action_done(PlayerAction.MOVE)
        self.assertTrue(self.game.is_current_action_done(PlayerAction.MOVE))
