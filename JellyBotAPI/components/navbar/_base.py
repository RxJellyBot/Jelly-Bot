class NavBaseItem:
    def __init__(self, parent=None):
        self._parent = parent
        self._iter_current = self

    def __iter__(self):
        while self._iter_current is not None:
            yield self._iter_current
            self._iter_current = self._iter_current.parent

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
