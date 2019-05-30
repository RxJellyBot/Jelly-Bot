from .holder import NavItemsHolder
from .dropdown import NavDropdown
from .entry import NavEntry
from .divider import NavDivider


def nav_items_factory(cls, current_path, **kwargs):
    if "link" in kwargs:
        kwargs["active"] = current_path == kwargs["link"]
    return cls(**kwargs)
