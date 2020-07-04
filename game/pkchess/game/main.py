from dataclasses import dataclass, field
from typing import List, Dict, Optional

from bson import ObjectId

from game.pkchess.exception import GameActionSubmittedError, GamePlayerInsufficientError
from game.pkchess.flags import PlayerAction
from game.pkchess.map import Map
from .player import PlayerEntry
from .base import Game

__all__ = ["RunningGame"]


@dataclass
class RunningGame(Game):
    map: Map
    players: List[PlayerEntry]

    current_idx: int = 0
    current_rounds: int = 1
    current_action_performed: Dict[PlayerAction, bool] = field(init=False)

    def __post_init__(self):
        if len(self.players) < 2:
            raise GamePlayerInsufficientError()

        self.current_action_performed = {action: False for action in PlayerAction}

    @property
    def current_player(self) -> PlayerEntry:
        return self.players[self.current_idx]

    def is_current_action_done(self, action: PlayerAction):
        return self.current_action_performed[action]

    def record_action_done(self, action: PlayerAction):
        if self.current_action_performed[action]:
            raise GameActionSubmittedError(action)

        self.current_action_performed[action] = True

    def current_player_finished(self):
        # Roll current player index
        self.current_idx += 1
        if self.current_idx >= len(self.players):
            self.current_idx = 0
            self.current_rounds += 1

        # Reset action performed status
        self.current_action_performed = {action: False for action in PlayerAction}

    def get_player_by_oid(self, player_oid: ObjectId) -> Optional[PlayerEntry]:
        for player in self.players:
            if player.player_oid == player_oid:
                return player

        return None
