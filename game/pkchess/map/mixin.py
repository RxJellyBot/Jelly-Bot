from abc import abstractmethod, ABC

__all__ = ["ConvertibleMapMixin"]


class ConvertibleMapMixin(ABC):
    @abstractmethod
    def to_map(self, players=None, player_location=None):
        """
        Convert the current object to a :class:`game.pkchess.map.Map`.

        ``players`` is a :class:`dict` where
            **key** is the OID of the player

            **value** is the :class:`game.pkchess.character.Character` of the player

        ``player_location`` is a :class:`dict` where
            **key** is the OID of the player

            **value** is the :class:`game.pkchess.map.MapCoordinate` of the player

        :param players: dict of the player's character
        :param player_location: dict of the player's location
        :return: converted `Map`
        """
        raise NotImplementedError()
