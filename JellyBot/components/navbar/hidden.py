from .firstlevel import NavFirstLevelItem


class NavHidden(NavFirstLevelItem):
    def __init__(self, label, link, active=False, parent=None):
        super().__init__(label, active, parent, link)

    # noinspection PyMethodMayBeStatic
    def to_html(self):
        return ""
