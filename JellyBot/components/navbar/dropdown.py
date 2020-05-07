from .entry import NavEntry, NavFirstLevelItem
from ._base import NavBaseItem


class NavDropdown(NavFirstLevelItem):
    def __init__(self, label, parent=None, active=False, link=None):
        super().__init__(label, active, parent, link)
        self._items = []

    @property
    def active(self) -> bool:
        return None or self.active_item

    @property
    def active_item(self):
        for item in self.items:
            if hasattr(item, "active") and item.active:
                return item

        return None

    @property
    def items(self):
        return self._items

    def add_item(self, item: NavBaseItem):
        item.parent = self
        self.items.append(item)

        return item

    def active_cls_str(self):
        return "active" if self.active else ""

    def to_html(self, num):
        # Dropdown button setup
        s = f'<li class="nav-item dropdown {self.active_cls_str()}">'
        s += f'<a class="nav-link dropdown-toggle" id="dropdown{num}" data-toggle="dropdown"' \
            f'aria-haspopup="true" aria-expanded="false">{self.label}</a>'

        s += f'<div class="dropdown-menu" aria-labelledby="dropdown{num}">'

        # Generate HTML for dropdown menu
        for item in self.items:
            if isinstance(item, NavDropdown):
                raise ValueError("Nested dropdown is not allowed.")
            elif isinstance(item, NavEntry):
                s += item.to_html(True)
            elif hasattr(item, "to_html"):
                # noinspection PyCallingNonCallable
                s += item.to_html()
        s += '</div></li>'

        return s

    def to_bread(self, active_link=None):
        s = super().to_bread(self.link)
        if self.active_item:
            s += self.active_item.to_bread()

        return s
