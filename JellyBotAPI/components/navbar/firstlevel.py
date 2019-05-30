from ._base import NavBaseItem


class NavFirstLevelItem(NavBaseItem):
    def __init__(self, label, active=False, parent=None, link=None):
        super().__init__(parent)
        self.label = label
        self.active = active
        self.link = link

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
