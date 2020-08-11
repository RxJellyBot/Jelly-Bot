from abc import ABC
from dataclasses import dataclass

from bson import ObjectId

__all__ = ["Game"]


@dataclass
class Game(ABC):
    """
    Base object of a game.
    """
    channel_oid: ObjectId
