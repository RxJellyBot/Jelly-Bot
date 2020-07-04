from random import Random
from dataclasses import dataclass, field
from typing import Optional, Dict

from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.exception import GameNotReadyError
from game.pkchess.map import MapTemplate
from .main import RunningGame
from .player import PlayerEntry
from .base import Game

__all__ = ["PendingGame"]


@dataclass
class PendingGame(Game):
    """
    Object representing a pending game.

    Pending game means that the game has not been started.

    For a pending game to be ready to start,
    the game should have 2+ players and decide the map to play.
    """
    RANDOM = Random()

    players: Dict[ObjectId, PlayerEntry] = field(default_factory=dict)  # key is the player's OID
    map_template: Optional[MapTemplate] = None

    @property
    def ready(self):
        """
        Check if the game is ready to be started.

        For the game to be ready to start, **ALL** of the following conditions must be fulfilled:

        - Player count >= 2

        - All players are ready (``ready`` is set to ``True``)

        - Map to be used is specified

        :return: game is ready to be started or not
        """
        players_sufficient = len(self.players) >= 2
        if not players_sufficient:
            return False

        players_ready = all(p.ready for p in self.players.values())
        if not players_ready:
            return False

        map_specified = self.map_template is not None
        if not map_specified:
            return False

        return True

    def add_player(self, player_oid: ObjectId, character: Character) -> bool:
        """
        Add a player to the game. Existence of the character should be checked **BEFORE** the call of this method.

        The name of the character will be directly used, without correcting the case.

        Returns ``True`` if the player joined the game; ``False`` if the player is already in the game.

        :param player_oid: OID of the player
        :param character: name of the character to be used for the player
        :return: if the player is added
        """
        if player_oid in self.players:
            return False

        self.players[player_oid] = PlayerEntry(player_oid, character)
        return True

    def player_ready(self, player_oid: ObjectId, *, ready: bool = True):
        """
        Set the player's ready status.

        Returns ``True`` if the ready state is correctly updated. ``False`` if the player does not exist.

        :param player_oid: OID of the player
        :param ready: new ready status. default to `True`
        :return: if the ready status is updated
        """
        if player_oid not in self.players:
            return False

        self.players[player_oid].ready = ready
        return True

    def start_game(self) -> RunningGame:
        """
        Start the current game. Converts this :class:`PendingGame` to :class:`RunningGame`.

        The order of the players of the returned :class:`RunningGame` will be randomized.

        :return: a `RunningGame` for the actual running game.
        :raises GameNotReadyError: if the game is not yet ready
        """
        if not self.ready:
            raise GameNotReadyError()

        players = list(self.players.values())
        self.RANDOM.shuffle(players)

        return RunningGame(
            self.channel_oid,
            self.map_template.to_map(
                players={plyr_oid: plyr_entry.character for plyr_oid, plyr_entry in self.players.items()}
            ),
            players
        )
