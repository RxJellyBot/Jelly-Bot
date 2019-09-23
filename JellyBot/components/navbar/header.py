from ._base import NavBaseItem


class NavHeader(NavBaseItem):
    def __init__(self, parent, label: str):
        super().__init__(parent)
        self._label = label

    @property
    def label(self) -> str:
        return self._label

    def to_html(self):
        return f'<h6 class="dropdown-header">{self.label}</h6>'
