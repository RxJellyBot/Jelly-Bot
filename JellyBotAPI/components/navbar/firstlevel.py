from abc import ABC

from ._base import NavBaseItem


class NavFirstLevelItem(NavBaseItem, ABC):
    def __init__(self, label, active=False, parent=None, link=None):
        super().__init__(parent)
        self._label = label
        self._active = active
        self._link = link

    @property
    def label(self):
        return self._label

    @property
    def active(self):
        return self._active

    @property
    def link(self):
        return self._link

    def active_cls_str(self):
        return "active" if self.active else ""

    def active_acc_str(self):
        return '<span class="sr-only">(current)</span>' if self.active else ''

    def to_bread(self, active_link=None):
        def get_content(additional):
            s = self.label
            if additional is not None:
                s = f'<a href="{additional}">{s}</a>'

            return s

        if self.active:
            return f'<li class="breadcrumb-item active" aria-current="page">{get_content(active_link)}</li>'
        else:
            return f'<li class="breadcrumb-item">{get_content(self.link)}</li>'
