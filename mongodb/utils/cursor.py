class ExtendedCursor:
    def __init__(self, cursor, parse_cls=None):
        self._cursor = cursor
        self._parse_cls = parse_cls

    def __iter__(self):
        for dict_ in self._cursor:
            o = self._parse_cls(**dict_, from_db=True)
            yield o

    def sort(self, key_or_list, direction=None):
        self._cursor = self._cursor.sort(key_or_list, direction)
        return self

    @property
    def alive(self):
        return self._cursor.alive
