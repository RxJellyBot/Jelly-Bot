from dataclasses import dataclass
from typing import List

from bson import ObjectId

from game.pkchess.map import Map


@dataclass
class RunningGame:
    channel_oid: ObjectId
    map: Map
    players: List[ObjectId]

    current_idx: int = 0

    @property
    def current_player(self) -> ObjectId:
        return self.players[self.current_idx]
