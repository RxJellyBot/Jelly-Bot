from typing import Dict, Optional

from bson import ObjectId

from mixin import ClearableMixin
from game.pkchess.flags import GameCreationResult
from game.pkchess.game import PendingGame, RunningGame
from game.pkchess.utils.character import is_character_exists

__all__ = ["GameController"]


class GameController(ClearableMixin):
    _pending_games: Dict[ObjectId, PendingGame] = {}
    _running_games: Dict[ObjectId, RunningGame] = {}

    @classmethod
    def clear(cls):
        cls._pending_games = {}
        cls._running_games = {}

    @classmethod
    def join_pending_game(cls, channel_oid: ObjectId, player_oid: ObjectId, character_name: str) -> GameCreationResult:
        """
        Join a pending game. If there is no pending game in the channel yet, automatically create one.

        :param channel_oid: channel OID of the pending game
        :param player_oid: OID of the player to join the pending game
        :param character_name: name of the character for the player to use
        :return: pending game join result
        """
        if not is_character_exists(character_name):
            return GameCreationResult.X_CHARACTER_NOT_EXIST

        if channel_oid in cls._pending_games:
            added = cls._pending_games[channel_oid].add_player(player_oid, character_name)

            return GameCreationResult.O_JOINED if added else GameCreationResult.X_ALREADY_JOINED

        pending_game = PendingGame(channel_oid)
        pending_game.add_player(player_oid, character_name)
        cls._pending_games[channel_oid] = pending_game
        return GameCreationResult.O_CREATED

    @classmethod
    def get_pending_game(cls, channel_oid: ObjectId) -> Optional[PendingGame]:
        return cls._pending_games.get(channel_oid)

    @classmethod
    def pending_game_set_map(cls, channel_oid: ObjectId, map_template_name: str):
        pass

    @classmethod
    def start_game(cls):

        pass
