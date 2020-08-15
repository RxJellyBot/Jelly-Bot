from dataclasses import dataclass

from bson import ObjectId
from game.pkchess.character import Character

__all__ = ("PlayerEntry",)


@dataclass
class PlayerEntry:
    player_oid: ObjectId
    character: Character
    ready: bool = False

    def __eq__(self, other):
        if not isinstance(other, PlayerEntry):
            return False

        return self.player_oid == other.player_oid

    def __hash__(self):
        return hash(self.player_oid)
