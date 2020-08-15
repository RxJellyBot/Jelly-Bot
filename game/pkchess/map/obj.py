from random import Random
from dataclasses import dataclass, InitVar
from typing import List, Dict, Optional, Set, Tuple, Iterable

from bson import ObjectId

from game.pkchess.character import Character
from game.pkchess.exception import (
    MapTooFewPointsError, MapDimensionTooSmallError, MapShapeMismatchError, MapTooManyPlayersError,
    MapPointUnspawnableError, SpawnPointOutOfMapError, NoPlayerSpawnPointError, UnknownResourceTypeError,
    CoordinateOutOfBoundError, GamePlayerNotFoundError, MoveDestinationOutOfMapError, CenterOutOfMapError,
    PathNotFoundError, PathSameDestinationError, PathEndOutOfMapError
)
from game.pkchess.flags import MapPointStatus, MapPointResource
from game.pkchess.objbase import BattleObject

from .mixin import ConvertibleMapMixin

__all__ = ("MapPoint", "MapCoordinate", "MapTemplate", "Map",)


@dataclass
class MapCoordinate:
    """Represents the coordinate of a map point."""
    X: int
    Y: int

    def apply_offset(self, x_offset: int, y_offset: int) -> 'MapCoordinate':
        """
        Return a new coordinate object which the offsets are applied.

        Note that ``y_offset`` will be reversed to reflect the correct coordinate on the map.

        > Map coordinate starts from left-top side. Right to increase X; **DOWN** to increase Y.

        > However, offset starts from center. Right to increase X; **UP** to increase Y.

        :param x_offset: offset for X
        :param y_offset: offset for Y
        :return: new offset-applied coordinate
        :raises CoordinateOutOfBoundError: if the new coordinate will be negative value after applying the offsets
        """
        new_obj = MapCoordinate(self.X + x_offset, self.Y - y_offset)

        if new_obj.X < 0 or new_obj.Y < 0:
            raise CoordinateOutOfBoundError()

        return new_obj

    def distance(self, other: 'MapCoordinate'):
        return abs(self.X - other.X) + abs(self.Y - other.Y)

    def __hash__(self):
        return hash((self.X, self.Y))

    def __eq__(self, other):
        if not isinstance(other, MapCoordinate):
            return False

        return self.X == other.X and self.Y == other.Y


@dataclass
class MapPoint:
    """Represents a map point."""
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
    RANDOM = Random()

    width: int
    height: int
    points: List[List[MapPoint]]
    resources: Dict[MapPointResource, List[MapCoordinate]]
    template: MapTemplate

    player_location: Dict[ObjectId, MapCoordinate] = None
    players: InitVar[Optional[Set[ObjectId]]] = None

    def __post_init__(self, players: Dict[ObjectId, Character]):
        if not self.player_location:
            self.player_location = {}
        else:
            for coord in self.player_location.values():
                self.points[coord.X][coord.Y].status = MapPointStatus.PLAYER

        if not self.player_location and players:
            player_coords: Set[MapCoordinate] = {pt.coord for pt in self.points_flattened
                                                 if pt.status == MapPointStatus.PLAYER}
            player_actual_count = len(players)
            player_deployable_count = len(player_coords)

            if player_actual_count > player_deployable_count:
                raise MapTooManyPlayersError(player_deployable_count, player_actual_count)

            # Randomly deploy player to deployable location
            # --- Cast to list to use `random.shuffle()` because dict and set usually is somehow ordered
            players = list(players.items())
            player_coords: List[MapCoordinate] = list(player_coords)
            self.RANDOM.shuffle(player_coords)
            self.RANDOM.shuffle(players)
            while players:
                player_oid, player_character = players.pop()
                coord = player_coords.pop()
                self.player_location[player_oid] = coord
                self.points[coord.X][coord.Y].status = MapPointStatus.PLAYER
                self.points[coord.X][coord.Y].obj = player_character

        # Fill the rest of the deployable location to be empty spot
        if self.player_location:
            occupied_coords: Set[MapCoordinate] = set(self.player_location.values())

            empty_player_coords: Set[MapCoordinate] = {pt.coord for pt in self.points_flattened
                                                       if pt.status == MapPointStatus.PLAYER}
            empty_player_coords.difference_update(occupied_coords)

            for coord in empty_player_coords:
                self.points[coord.X][coord.Y].status = MapPointStatus.EMPTY

    def player_move(self, player_oid: ObjectId, x_offset: int, y_offset: int, max_move: float) -> bool:
        """
        Move the player using the given coordinate offset.

        Returns ``False`` if the destination is not an empty spot. Otherwise, move the player and return ``True``.

        ``max_move`` will be rounded.

        :param player_oid: OID of the player
        :param x_offset: offset of X
        :param y_offset: offset of Y
        :param max_move: maximum count of the moves allowed
        :return: if the movement succeed
        :raises GamePlayerNotFoundError: the player to be moved not found
        :raises MoveDestinationOutOfMapError: movement destination is out of map
        :raises PathNotFoundError: path from the player's location to the destination not found
        """
        # Check player existence
        if player_oid not in self.player_location:
            raise GamePlayerNotFoundError()

        # Apply the movement offset
        try:
            origin = self.player_location[player_oid]
            destination = self.player_location[player_oid].apply_offset(x_offset, y_offset)
        except CoordinateOutOfBoundError:
            raise MoveDestinationOutOfMapError()

        # Check if the new coordinate is out of map
        if destination.X >= self.width or destination.Y >= self.height:
            raise MoveDestinationOutOfMapError()

        original_point = self.points[origin.X][origin.Y]
        new_point = self.points[destination.X][destination.Y]

        # Check if the new coordinate is not empty
        if new_point.status != MapPointStatus.EMPTY:
            return False

        # Check if the path is connected and the destination is empty
        if not self.get_shortest_path(origin, destination, round(max_move)):
            raise PathNotFoundError(origin, destination)

        # Move the player & update related variables
        self.player_location[player_oid] = destination

        new_point.obj = original_point.obj
        new_point.status = MapPointStatus.PLAYER
        original_point.obj = None
        original_point.status = self.template.points[origin.X][origin.Y]
        if original_point.status == MapPointStatus.PLAYER:
            original_point.status = MapPointStatus.EMPTY

        return True

    def get_shortest_path(self, origin: MapCoordinate, destination: MapCoordinate, max_length: int) \
            -> Optional[List[MapCoordinate]]:
        """
        Get the first-found shortest path from ``origin`` to ``destination``.

        ``max_length`` must be a positive integer. (No runtime check)

        Returns ``None`` if

        - the point status of ``destination`` is not ``MapPointStatus.EMPTY``.

        - the path is not found.

        - the path length is longer than ``max_length`` but not yet reached the ``destination``.

        :param origin: origin of the path
        :param destination: desired destination
        :param max_length: max length of the path
        :return: path from `origin` to `destination` if found. `None` on not found
        :raises PathSameDestinationError: if `origin` and `destination` are the same
        """
        if origin == destination:
            raise PathSameDestinationError()

        origin_out_of_map = origin.X >= self.width or origin.Y > self.height
        destination_out_of_map = destination.X >= self.width or destination.Y > self.height
        if origin_out_of_map or destination_out_of_map:
            raise PathEndOutOfMapError(origin, destination, self.width, self.height)

        # Check if the destination point is not empty
        if self.points[destination.X][destination.Y].status != MapPointStatus.EMPTY:
            return None

        return self._get_shortest_path(origin, destination, max_length, [[origin]])

    def _path_constructible(self, path: List[MapCoordinate], new_path_tail: MapCoordinate, destination: MapCoordinate):
        if new_path_tail.X >= self.width or new_path_tail.Y >= self.height:
            return False

        tail = path[-1]

        original_distance = tail.distance(destination)
        new_distance = new_path_tail.distance(destination)

        not_on_path = new_path_tail not in path
        distance_le = new_distance <= original_distance
        point_empty = self.points[new_path_tail.X][new_path_tail.Y].status == MapPointStatus.EMPTY

        return not_on_path and distance_le and point_empty

    def _get_shortest_path(self, origin: MapCoordinate, destination: MapCoordinate, max_length: int,
                           paths: List[List[MapCoordinate]] = None) -> Optional[List[MapCoordinate]]:
        """Helper method of ``self.get_shortest_path()``."""
        new_paths = []
        for path in paths:
            # Extend every path to left, right, up, down

            # Terminate if the current path without adding the new point is longer than allowed
            if len(path) > max_length:
                return None

            tail = path[-1]

            new_pts = [
                tail.apply_offset(1, 0),  # right
                tail.apply_offset(-1, 0),  # left
                tail.apply_offset(0, 1),  # up
                tail.apply_offset(0, -1)  # down
            ]

            for new_pt in new_pts:
                if self._path_constructible(path, new_pt, destination):
                    if new_pt == destination:
                        return path + [new_pt]

                    new_paths.append(path + [new_pt])

        if not new_paths:
            # Dead-end, returns `None`
            return None
        else:
            # Search deeper
            return self._get_shortest_path(origin, destination, max_length, new_paths)

    def get_points(self, center: MapCoordinate, offsets: Iterable[Tuple[int, int]]) -> List[MapPoint]:
        if center.X >= self.width or center.X < 0 or center.Y >= self.height or center.Y < 0:
            raise CenterOutOfMapError()

        pt_coord = []
        for offset_x, offset_y in offsets:
            try:
                new_coord = center.apply_offset(offset_x, offset_y)
            except CoordinateOutOfBoundError:
                continue

            if new_coord.X >= self.width or new_coord.Y >= self.height:
                continue

            pt_coord.append(new_coord)

        pts = [self.points[coord.X][coord.Y] for coord in pt_coord]

        return pts

    @property
    def points_flattened(self) -> List[MapPoint]:
        """
        Get the 1D array of the points flattened from ``self.points``.

        :return: flattened array of `self.points`

        .. seealso::
            https://stackoverflow.com/a/29244327/11571888
        """
        return sum(self.points, [])
