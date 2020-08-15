from django.utils.translation import gettext_lazy as _

__all__ = ("MapPoint",)


class MapPoint:
    UNAVAILABLE = _("Unavailable")
    EMPTY = _("Empty")
    PLAYER = _("Player")
    CHEST = _("Chest")
    MONSTER = _("Monster")
    FIELD_BOSS = _("Field Boss")
