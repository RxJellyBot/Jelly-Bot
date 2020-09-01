"""Customized ``pymongo`` cursor."""
from typing import Generic, TypeVar, Type

from models import Model

T = TypeVar("T", bound=Model)  # pylint: disable=invalid-name


class ExtendedCursor(Generic[T]):
    """Customized ``pymongo`` cursor class."""

    def __init__(self, cursor, count, parse_cls: Type[T] = None):
        self._cursor = cursor
        self._count = count
        self._parse_cls = parse_cls

    def __iter__(self):
        for dict_ in self._cursor:
            if self._parse_cls:
                yield self._parse_cls(**dict_, from_db=True)
            else:
                yield dict_

    def __len__(self):
        return self._count

    def limit(self, limit) -> 'ExtendedCursor':
        """
        Limit the data to return from the actual cursor.

        This returns the cursor itself for the convenience of method chaining.

        This modifies the cursor itself.

        :param limit: max count of the data to return
        :return: limited cursor (this object)
        """
        if limit:
            self._cursor = self._cursor.limit(limit)
        return self

    @property
    def empty(self):
        """
        Check if this cursor is empty.

        :return: if this cursor is empty
        """
        return len(self) == 0
