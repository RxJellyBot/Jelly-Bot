from datetime import datetime, timedelta

import pytz
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def now_utc_aware():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)


def localtime(dt=None, tz=None):
    return timezone.localtime(dt, tz)


def is_tz_naive(dt) -> bool:
    return dt.tzinfo is None or dt.tzinfo.utcoffset(datetime.now()) is None


def t_delta_str(t_delta: timedelta):
    h = t_delta.seconds // 3600
    m = (t_delta.seconds - 3600 * h) // 60
    s = t_delta.seconds % 60

    if t_delta.days > 3:
        return _("{} Days {} H {:02} M {:02} S").format(t_delta.days, h, m, s)
    else:
        h += t_delta.days * 24
        return _("{} H {:02} M {:02} S").format(h, m, s)
