import random
from dataclasses import dataclass, InitVar
from typing import List, Dict, Optional, Set

from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.exception import (
    MapTooFewPointsError, MapDimensionTooSmallError, MapShapeMismatchError, MapTooManyPlayersError,
    MapPointUnspawnableError, SpawnPointOutOfMapError, NoPlayerSpawnPointError, UnknownResourceTypeError,
    CoordinateOutOfBoundError, GamePlayerNotFoundError, MoveDestinationOutOfMapError
)
from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.objbase import BattleObject

from .mixin import ConvertibleMapMixin

__all__ = ["MapPoint", "MapCoordinate", "MapTemplate", "Map"]


@dataclass
class MapCoordinate:
    """
    Represents the coordinate of a map point.
    """
    X: int
    Y: int

    def apply_offset(self, x_offset: int, y_offset: int) -> ('MapCoordinate', 'MapCoordinate'):
        """
        Apply the offsets of the coordinate to this coordinate object and return the original and the new coordinates.

        Note that the first coordinate object is a new object and the second coordinate object is the current object.

        :param x_offset: offset for X
        :param y_offset: offset for Y
        :return: a 2-tuple which the first is the original coordinate and the second is the current coordinate
        :raises CoordinateOutOfBoundError: if the new coordinate will be negative value after applying the offsets
        """
        original = MapCoordinate(self.X, self.Y)

        self.X += x_offset
        self.Y += y_offset

        if self.X < 0 or self.Y < 0:
            self.X -= x_offset
            self.Y -= y_offset
            raise CoordinateOutOfBoundError()

        return original, self

    def __hash__(self):
        return hash((self.X, self.Y))

    def __eq__(self, other):
        if not isinstance(other, MapCoordinate):
            return False

        return self.X == other.X and self.Y == other.Y


@dataclass
class MapPoint:
    """
    Represents a map point.
    """
    status: MapPointStatus
    coord: MapCoordinate
    obj: Optional[BattleObject] = None


@dataclass
class MapTemplate(ConvertibleMapMixin):
    """
    Map template.

    This could be converted to :class:`MapModel` and
    store to the database (initialize a game) by calling `to_model()`.

    Set ``bypass_map_chack`` to ``True`` to bypass the available map point check and the size check.
    This should be used only in tests.
    """
    MIN_WIDTH = 9
    MIN_HEIGHT = 9
    MIN_AVAILABLE_POINTS = 81

    width: int
    height: int
    points: List[List[MapPointStatus]]
    resources: Dict[MapPointResource, List[MapCoordinate]]

    bypass_map_chack: InitVar[bool] = False

    def _check_map_dimension(self):
        if self.width < MapTemplate.MIN_WIDTH or self.height < MapTemplate.MIN_HEIGHT:
            raise MapDimensionTooSmallError()

    def _check_available_points(self):
        available = sum(sum(1 if p.is_map_point else 0 for p in row) for row in self.points)
        if available < MapTemplate.MIN_AVAILABLE_POINTS:
            raise MapTooFewPointsError(MapTemplate.MIN_AVAILABLE_POINTS, available)

    def _check_player_spawn_point(self):
        if not any(any(p == MapPointStatus.PLAYER for p in row) for row in self.points):
            raise NoPlayerSpawnPointError()

    def _check_resource_points(self):
        for coords in self.resources.values():
            for coord in coords:
                x = coord.X
                y = coord.Y

                # Check out of map
                if x >= self.width or y >= self.height:
                    raise SpawnPointOutOfMapError()

                if not self.points[x][y].is_map_point:
                    raise MapPointUnspawnableError()

    def _check_dimension_point_matrix(self):
        try:
            self.points[self.width - 1][self.height - 1]
        except IndexError:
            raise MapShapeMismatchError()

    def __post_init__(self, bypass_map_chack: bool):
        if bypass_map_chack:
            return

        self._check_map_dimension()
        self._check_available_points()
        self._check_player_spawn_point()
        self._check_resource_points()
        self._check_dimension_point_matrix()

    def respawn(self):
        pass  # TODO: Game - game respawn object

    def to_map(self, *,
               players: Dict[ObjectId, Character] = None,
               player_location: Dict[ObjectId, MapCoordinate] = None) \
            -> 'Map':
        pts = []

        for x, pts_arr in enumerate(self.points):
            arr = []

            for y, pt in enumerate(pts_arr):
                arr.append(MapPoint(pt, MapCoordinate(x, y)))

            pts.append(arr)

        return Map(self.width, self.height, pts, self.resources, self,
                   players=players, player_location=player_location)

    @staticmethod
    def load_from_file(path: str) -> Optional['MapTemplate']:
        """
        Load the template from a map file.

        This parsing method checks logic error, but not the format error.

        If the map template is not found, return ``None``.

        .. seealso::
            See `doc/spec/map.md` for the specification of the map file.

        :param path: path of the file
        :return: a parsed `MapTemplate` or `None`
        """
        try:
            with open(path) as f:
                lines = f.read().split("\n")
        except FileNotFoundError:
            return None

        # Parse dimension
        width, height = [int(n) for n in lines.pop(0).split(" ", 2)]

        # Parse initial map points
        points: List[List[MapPointStatus]] = [[] for _ in range(width)]
        for y in range(height):
            for x, elem in zip(range(width), lines.pop(0)):
                points[x].append(MapPointStatus.cast(elem))

        # parse resource spawning location
        res_dict: Dict[MapPointResource, List[MapCoordinate]] = {}
        for line in lines:
            type_int, *coords = line.split(" ")

            try:
                res_type = MapPointResource.cast(type_int)
            except ValueError:
                raise UnknownResourceTypeError()

            coords = [coord.split(",", 2) for coord in coords]
            res_dict[res_type] = [MapCoordinate(int(x), int(y)) for x, y in coords]

        return MapTemplate(width, height, points, res_dict)


@dataclass
class Map:
    """
    Represents the map.

    If ``players`` has any element in it and ``player_location`` is empty,
    players will be randomly deployed to the point where the status is :class:`MapPointStatus.PLAYER`.

    The rest of the deployable points will be replaced with :class:`MapPointStatus.EMPTY`.

    If both ``player_location`` and ``players`` are given, ``players`` will be ignored.
    """
    width: int
    height: int
    points: List[List[MapPoint]]
    resources: Dict[MapPointResource, List[MapCoordinate]]
    template: MapTemplate

    player_location: Dict[ObjectId, MapCoordinate] = None
    players: InitVar[Optional[Set[ObjectId]]] = None

    def __post_init__(self, players: Dict[ObjectId, Character]):
        if not self.player_location and players:
            self.player_location = {}

            player_coords: Set[MapCoordinate] = {pt.coord for pt in self.points_flattened}
            player_actual_count = len(players)
            player_deployable_count = sum(map(lambda pt: pt.status == MapPointStatus.PLAYER, self.points_flattened))

            if player_actual_count > player_deployable_count:
                raise MapTooManyPlayersError(player_deployable_count, player_actual_count)

            # Randomly deploy player to deployable location
            # --- Cast to list to use `random.shuffle()` because dict and set usually is somehow ordered
            players = list(players.items())
            player_coords: List[MapCoordinate] = list(player_coords)
            random.shuffle(player_coords)
            random.shuffle(players)
            while players:
                player_oid, player_character = players.pop()
                coord = player_coords.pop()
                self.player_location[player_oid] = coord
                self.points[coord.X][coord.Y].status = MapPointStatus.PLAYER
                self.points[coord.X][coord.Y].obj = player_character

            # Fill the rest of the deployable location to be empty spot
            if player_coords:
                for coord in player_coords:
                    self.points[coord.X][coord.Y].status = MapPointStatus.EMPTY

    def player_move(self, player_oid: ObjectId, x_offset: int, y_offset: int) -> bool:
        """
        Move the player using the given coordinate offset.

        Returns ``False`` if the destination is not an empty spot. Otherwise, move the player and return ``True``.

        :param player_oid: OID of the player
        :param x_offset: offset of X
        :param y_offset: offset of Y
        :return: if the movement succeed
        :raises GamePlayerNotFoundError: the player to be moved not found
        :raises MoveDestinationOutOfMapError: movement destination is out of map
        """
        # Check player existence
        if player_oid not in self.player_location:
            raise GamePlayerNotFoundError()

        # Apply the movement offset
        try:
            original, current = self.player_location[player_oid].apply_offset(x_offset, y_offset)
        except CoordinateOutOfBoundError:
            raise MoveDestinationOutOfMapError()

        # Check if the new coordinate is out of map. Revert if this is true
        if current.X >= self.width or current.Y >= self.height:
            current.apply_offset(-x_offset, -y_offset)
            raise MoveDestinationOutOfMapError()

        original_point = self.points[original.X][original.Y]
        new_point = self.points[current.X][current.Y]

        # Check if the new coordinate is not empty. Revert if this is true
        if new_point.status != MapPointStatus.EMPTY:
            current.apply_offset(-x_offset, -y_offset)
            return False

        # Move the player
        new_point.obj = original_point.obj
        new_point.status = MapPointStatus.PLAYER
        original_point.obj = None
        original_point.status = self.template.points[original.X][original.Y]

        return True

    @property
    def points_flattened(self) -> List[MapPoint]:
        """
        Get the 1D array of the points flattened from ``self.points``.

        :return: flattened array of `self.points`

        .. seealso::
            https://stackoverflow.com/a/29244327/11571888
        """
        return sum(self.points, [])
