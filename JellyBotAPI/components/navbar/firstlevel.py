from ._base import NavBaseItem


class NavFirstLevelItem(NavBaseItem):
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

    def to_bread(self):
        if self.active:
            return f'<li class="breadcrumb-item active" aria-current="page">{self.label}</li>'
        else:
            s = self.label
            if self.link is not None:
                s = f'<a href="{self.link}">{s}</a>'
            return f'<li class="breadcrumb-item">{s}</li>'
