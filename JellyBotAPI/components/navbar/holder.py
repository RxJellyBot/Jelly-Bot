from typing import Union, List

from .entry import NavEntry, NavFirstLevelItem
from .dropdown import NavDropdown, NavBaseItem


class NavItemsHolder:
    def __init__(self, nav_items: Union[List[NavBaseItem], type(None)] = None):
        if nav_items is None:
            self.nav_items = []
        else:
            self.nav_items = nav_items

        self.active = None

    def __iter__(self):
        for item in self.nav_items:
            yield item

    def add_item(self, nav_item: NavFirstLevelItem):
        self.nav_items.append(nav_item)
        if nav_item.active:
            self.active = nav_item

    def to_html(self):
        dropdown_count = 0

        s = '<ul class="navbar-nav mr-auto">'
        for item in self.nav_items:
            if isinstance(item, NavEntry):
                s += item.to_html(False)
            elif isinstance(item, NavDropdown):
                dropdown_count += 1

                s += item.to_html(dropdown_count)
            else:
                raise ValueError(f"Unhandled class {item}.")
        s += '</ul>'

        return s

    def to_bread(self):
        if self.active is not None:
            s = '<ol class="breadcrumb">'
            lst = []
            for node in self.active:
                lst.append(node.to_bread())
            s += "".join(reversed(lst))
            s += '</ol>'
            return s
        else:
            return ''
