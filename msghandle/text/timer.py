from typing import List

from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from JellyBot.systemconfig import Bot
from extutils.dt import t_delta_str, now_utc_aware
from flags import BotFeature
from mongodb.factory import TimerManager, BotFeatureUsageDataManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageEventText


def process_timer_get(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    tmrs = TimerManager.get_timer(e.channel_oid, e.content)

    if tmrs.has_data:
        BotFeatureUsageDataManager.record_usage_async(BotFeature.TXT_TMR_GET, e.channel_oid, e.user_model.id)

        return [HandledMessageEventText(content=tmrs.to_string(e.user_model))]

    return []


def process_timer_notification(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    crs = TimerManager.get_notify(e.channel_oid)

    if not crs.empty:
        now = now_utc_aware()
        ret = [_("**{} timer(s) will time up in less than {} hrs!**").format(len(crs), Bot.Timer.NotifyWithinHours), ""]

        for tmr in crs:
            ret.append(_("{event} will time up after [{diff}]! (at {time})").format(
                event=tmr.title, diff=t_delta_str(tmr.get_target_time_diff(now)),
                time=localtime(tmr.target_time, e.user_model.config.tzinfo)
            ))

        return [HandledMessageEventText(content="\n".join(ret))]

    return []
