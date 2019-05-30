from ._base import NavBaseItem


class NavDivider(NavBaseItem):
    def __init__(self, parent):
        super().__init__(parent)

    # noinspection PyMethodMayBeStatic
    def to_html(self):
        return '<div class="dropdown-divider"></div>'
