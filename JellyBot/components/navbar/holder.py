import warnings
from typing import Union, List

from .entry import NavEntry, NavFirstLevelItem
from .dropdown import NavDropdown, NavBaseItem
from .hidden import NavHidden


class NavItemsHolder:
    def __init__(self, nav_items: Union[List[NavBaseItem], type(None)] = None):
        if nav_items is None:
            self._nav_items = []
        else:
            self._nav_items = nav_items

        self._active_item = None

    def __iter__(self):
        for item in self.nav_items:
            yield item

    @property
    def active_item(self):
        return self._active_item

    @active_item.setter
    def active_item(self, value):
        self._active_item = value

    @property
    def nav_items(self):
        return self._nav_items

    def add_item(self, nav_item: NavFirstLevelItem):
        self.nav_items.append(nav_item)
        if nav_item.active:
            self._active_item = nav_item

    def to_html(self):
        dropdown_count = 0

        s = '<ul class="navbar-nav mr-auto">'
        for item in self.nav_items:
            if isinstance(item, NavEntry):
                s += item.to_html(False)
            elif isinstance(item, NavDropdown):
                dropdown_count += 1

                s += item.to_html(dropdown_count)
            elif isinstance(item, NavHidden):
                pass
            else:
                raise ValueError(f"Unhandled class {item}.")
        s += '</ul>'

        return s

    def to_bread(self):
        if self.active_item:
            s = '<ol class="breadcrumb">'
            lst = []
            # From deepest to shallowest
            for node in self.active_item:
                lst.append(node.to_bread())
            s += "".join(reversed(lst))
            s += '</ol>'
            return s
        else:
            warnings.warn("No breadcrumb for the page generated just now!")
            return ''
