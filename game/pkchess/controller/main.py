from typing import Dict, Optional, Union, List, Tuple

from bson import ObjectId

from mixin import ClearableMixin
from game.pkchess.character import Character
from game.pkchess.controller import DamageCalculator, Damage
from game.pkchess.exception import MoveDestinationOutOfMapError, PathNotFoundError
from game.pkchess.flags import (
    GameCreationResult, GameMapSetResult, GameStartResult, GameReadyResult, PlayerActionResult, PlayerAction,
    SkillDirection
)
from game.pkchess.game import PendingGame, RunningGame
from game.pkchess.res import get_map_template, skills
from game.pkchess.utils.character import get_character_template

__all__ = ["GameController"]


class GameController(ClearableMixin):
    # DRAFT: Game sync - fetch the running games in the database
    _pending_games: Dict[ObjectId, PendingGame] = {}
    _running_games: Dict[ObjectId, RunningGame] = {}

    @classmethod
    def clear(cls):
        cls._pending_games = {}
        cls._running_games = {}

        # DRAFT: Game sync - Clear the database

    @classmethod
    def join_pending_game(cls, channel_oid: ObjectId, player_oid: ObjectId, character_name: str) -> GameCreationResult:
        """
        Join a pending game. If there is no pending game in the channel yet, automatically create one.

        :param channel_oid: channel OID of the pending game
        :param player_oid: OID of the player to join the pending game
        :param character_name: name of the character for the player to use
        :return: pending game join result
        """
        chara_template = get_character_template(character_name)
        if not chara_template:
            return GameCreationResult.X_CHARACTER_NOT_EXIST

        if channel_oid in cls._pending_games:
            added = cls._pending_games[channel_oid].add_player(player_oid, Character(chara_template))

            return GameCreationResult.O_JOINED if added else GameCreationResult.X_ALREADY_JOINED

        pending_game = PendingGame(channel_oid)
        pending_game.add_player(player_oid, Character(chara_template))
        cls._pending_games[channel_oid] = pending_game
        return GameCreationResult.O_CREATED

    @classmethod
    def get_pending_game(cls, channel_oid: ObjectId) -> Optional[PendingGame]:
        return cls._pending_games.get(channel_oid)

    @classmethod
    def pending_game_set_map(cls, channel_oid: ObjectId, map_template_name: str) -> GameMapSetResult:
        game = cls.get_pending_game(channel_oid)
        if not game:
            return GameMapSetResult.X_GAME_NOT_FOUND

        template = get_map_template(map_template_name)
        if not template:
            return GameMapSetResult.X_TEMPLATE_NOT_FOUND

        game.map_template = template
        return GameMapSetResult.O_SET

    @classmethod
    def pending_game_ready(cls, channel_oid: ObjectId, player_oid: ObjectId, *, ready: bool = True) -> GameReadyResult:
        game = cls.get_pending_game(channel_oid)
        if not game:
            return GameReadyResult.X_GAME_NOT_FOUND

        return GameReadyResult.O_UPDATED \
            if game.player_ready(player_oid, ready=ready) \
            else GameReadyResult.X_PLAYER_NOT_FOUND

    @classmethod
    def start_game(cls, channel_oid: ObjectId) -> GameStartResult:
        pending_game = cls.get_pending_game(channel_oid)
        if not pending_game:
            return GameStartResult.X_GAME_NOT_FOUND

        if not pending_game.ready:
            return GameStartResult.X_GAME_NOT_READY

        if channel_oid in cls._running_games:
            return GameStartResult.X_GAME_EXISTED

        cls._running_games[channel_oid] = pending_game.start_game()
        del cls._pending_games[channel_oid]

        return GameStartResult.O_STARTED

    @classmethod
    def get_running_game(cls, channel_oid: ObjectId) -> Optional[RunningGame]:
        return cls._running_games.get(channel_oid)

    @classmethod
    def set_running_game(cls, channel_oid: ObjectId, running_game: RunningGame):
        """
        **THIS SHOULD BE USED ONLY FOR THE TESTS**

        Directly set a running game to the cache.

        :param channel_oid: OID of the channel to be set the game
        :param running_game: game to be set for the channel
        """
        cls._running_games[channel_oid] = running_game

    @classmethod
    def _player_action_pre_check(cls, channel_oid: ObjectId, player_oid: ObjectId,
                                 actions: Union[PlayerAction, List[PlayerAction]]) \
            -> Union[PlayerActionResult, Tuple[PlayerAction, RunningGame]]:
        """
        Pre-check the player action(s).

        If ``actions`` is a list, then the check will be performed sequentially.
        Failing results will be returned if all of the actions are failed to perform.
        If any of the action can be performed, then the action perform permit check will be considered passed.

        This checks

        - If the game has started / exists

        - Player action is performed

        - Player exists / is current

        Returns a 2-tuple containing the action allowed to be performed and a :class:`RunningGame`.
        Otherwise, returns :class:`PlayerActionResult`.

        ----------

        Possible :class:`PlayerActionResult` to be returned:

        - :class:`PlayerActionResult.X_GAME_NOT_STARTED`

        - :class:`PlayerActionResult.X_GAME_NOT_FOUND`

        - :class:`PlayerActionResult.X_ALREADY_PERFORMED`

        - :class:`PlayerActionResult.X_PLAYER_NOT_EXISTS`

        - :class:`PlayerActionResult.X_PLAYER_NOT_CURRENT`

        :param channel_oid: channel OID of the game
        :param player_oid: player OID of the game
        :param actions: action(s) to be performed
        :return: a `RunningGame` or `PlayerActionResult`
        """
        # Game existence check
        game = cls.get_running_game(channel_oid)
        if not game:
            if cls.get_pending_game(channel_oid):
                return PlayerActionResult.X_GAME_NOT_STARTED

            return PlayerActionResult.X_GAME_NOT_FOUND

        # Action done check
        if isinstance(actions, PlayerAction):
            actions = [actions]

        try:
            action = next(action for action in actions if not game.is_current_action_done(action))
        except StopIteration:
            return PlayerActionResult.X_ALREADY_PERFORMED

        # Player existence check
        if not any(p_entry.player_oid == player_oid for p_entry in game.players):
            return PlayerActionResult.X_PLAYER_NOT_EXISTS

        # Current player check
        if game.current_player.player_oid != player_oid:
            return PlayerActionResult.X_PLAYER_NOT_CURRENT

        return action, game

    @classmethod
    def player_move(cls, channel_oid: ObjectId, player_oid: ObjectId, x_offset: int, y_offset: int) \
            -> PlayerActionResult:
        """
        Perform move action for a player.

        ----------

        Possible :class:`PlayerActionResult` to be returned:

        - :class:`PlayerActionResult.X_GAME_NOT_STARTED`

        - :class:`PlayerActionResult.X_GAME_NOT_FOUND`

        - :class:`PlayerActionResult.X_ALREADY_PERFORMED`

        - :class:`PlayerActionResult.X_PLAYER_NOT_EXISTS`

        - :class:`PlayerActionResult.X_PLAYER_NOT_CURRENT`

        - :class:`PlayerActionResult.X_TOO_MANY_MOVES`

        - :class:`PlayerActionResult.X_DESTINATION_NOT_EMPTY`

        - :class:`PlayerActionResult.X_DESTINATION_OUT_OF_MAP`

        - :class:`PlayerActionResult.X_MOVE_PATH_NOT_FOUND`

        - :class:`PlayerActionResult.O_ACTED`

        :param channel_oid: channel OID of the game
        :param player_oid: player OID of the game
        :param x_offset: X offset of the movement
        :param y_offset: Y offset of the movement
        :return: result of the movement
        """
        pre_check_result = cls._player_action_pre_check(channel_oid, player_oid, PlayerAction.MOVE)
        if isinstance(pre_check_result, PlayerActionResult):
            return pre_check_result

        action, game = pre_check_result

        if x_offset + y_offset > game.current_player.character.MOV:
            return PlayerActionResult.X_TOO_MANY_MOVES

        try:
            if not game.map.player_move(player_oid, x_offset, y_offset, game.current_player.character.MOV):
                return PlayerActionResult.X_DESTINATION_NOT_EMPTY
        except MoveDestinationOutOfMapError:
            return PlayerActionResult.X_DESTINATION_OUT_OF_MAP
        except PathNotFoundError:
            return PlayerActionResult.X_MOVE_PATH_NOT_FOUND

        game.record_action_done(action)
        return PlayerActionResult.O_ACTED

    @classmethod
    def player_skill(cls, channel_oid: ObjectId, player_oid: ObjectId,
                     skill_idx: int, skill_direction: SkillDirection) -> (PlayerActionResult, List[Damage]):
        """
        Use a skill for a player.

        ----------

        Possible :class:`PlayerActionResult` to be returned:

        - :class:`PlayerActionResult.X_GAME_NOT_STARTED`

        - :class:`PlayerActionResult.X_GAME_NOT_FOUND`

        - :class:`PlayerActionResult.X_ALREADY_PERFORMED`

        - :class:`PlayerActionResult.X_PLAYER_NOT_EXISTS`

        - :class:`PlayerActionResult.X_PLAYER_NOT_CURRENT`

        - :class:`PlayerActionResult.X_SKILL_IDX_OUT_OF_BOUND`

        - :class:`PlayerActionResult.X_SKILL_NOT_FOUND`

        - :class:`PlayerActionResult.O_ACTED`

        :param channel_oid: channel OID of the game
        :param player_oid: player OID of the game
        :param skill_idx: index of the skill
        :param skill_direction: direction of the skill
        :return: result of the skill
        """
        dmgs = []

        pre_check_result = cls._player_action_pre_check(
            channel_oid, player_oid, [PlayerAction.SKILL_1, PlayerAction.SKILL_2])
        if isinstance(pre_check_result, PlayerActionResult):
            return pre_check_result, dmgs

        action, game = pre_check_result

        skill_ids = game.current_player.character.skill_ids
        if skill_idx < 0 or skill_idx >= len(skill_ids):
            return PlayerActionResult.X_SKILL_IDX_OUT_OF_BOUND, dmgs

        skill_id = skill_ids[skill_idx]
        skill = skills.get(skill_id)
        if not skill:
            return PlayerActionResult.X_SKILL_NOT_FOUND, dmgs

        for pt in game.map.get_points(game.map.player_location[player_oid],
                                      skill_direction.rotate_offsets(skill.range)):
            obj = pt.obj
            if obj:
                dmgs.append(DamageCalculator.deal_damage(game.current_player.character, obj))

        game.record_action_done(action)
        return PlayerActionResult.O_ACTED, dmgs

    @classmethod
    def on_turn_completed(cls):
        pass  # TODO: Game - on turn completed - call the checking method for every turn (respawn) (implement & test)
