from .firstlevel import NavFirstLevelItem


class NavEntry(NavFirstLevelItem):
    def __init__(self, label, link, disabled=False, active=False, parent=None):
        super().__init__(label, active, parent, link)
        self.disabled = disabled

    def disabled_cls_str(self):
        return "disabled" if self.disabled else ""

    def to_html(self, in_dropdown):
        if in_dropdown:
            return f'<a class="dropdown-item {self.active_cls_str()} {self.disabled_cls_str()}" href="{self.link}">' \
                f'{self.label}</a>'
        else:
            return f'<li class="nav-item {self.active_cls_str()}">' \
                f'<a class="nav-link {self.disabled_cls_str()}" href="{self.link}">{self.label}' \
                f'{self.active_acc_str()}' \
                f'</a></li>'
