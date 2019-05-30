from .entry import NavEntry, NavFirstLevelItem
from ._base import NavBaseItem
from .divider import NavDivider


class NavDropdown(NavFirstLevelItem):
    def __init__(self, label, active=False, parent=None):
        super().__init__(label, active, parent, link=None)
        self.items = []

    def add_item(self, item: NavBaseItem):
        item.parent = self
        self.items.append(item)

    def to_html(self, num):
        s = f'<li class="nav-item dropdown {self.active_cls_str()}">'
        s += f'<a class="nav-link dropdown-toggle" id="dropdown{num}" data-toggle="dropdown"' \
             f'aria-haspopup="true" aria-expanded="false">{self.label}</a>'

        s += f'<div class="dropdown-menu" aria-labelledby="dropdown{num}">'

        for item in self.items:
            if isinstance(item, NavDropdown):
                raise ValueError("Nested dropdown is not allowed.")
            elif isinstance(item, NavEntry):
                s += item.to_html(True)
            elif isinstance(item, NavDivider):
                s += item.to_html()
        s += '</div></li>'

        return s
