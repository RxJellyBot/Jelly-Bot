class CursorWithCount:
    def __init__(self, cursor, count, parse_cls=None):
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

    def sort(self, key_or_list, direction=None):
        self._cursor = self._cursor.sort(key_or_list, direction)
        return self

    def limit(self, limit):
        if limit:
            self._cursor = self._cursor.limit(limit)
        return self

    @property
    def empty(self):
        return len(self) == 0
