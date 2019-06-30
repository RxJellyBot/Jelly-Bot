class CheckableCursor:
    def __init__(self, cursor, parse_cls=None):
        self._cursor = cursor
        self._parse_cls = parse_cls

    def __iter__(self):
        for dict_ in self._cursor:
            o = self._parse_cls(**dict_, from_db=True)
            yield o

    @property
    def empty(self):
        return self._cursor.count() == 0
