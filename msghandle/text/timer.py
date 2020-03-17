from typing import List

from django.utils.translation import gettext_lazy as _

from JellyBot.systemconfig import Bot
from extutils.dt import t_delta_str, now_utc_aware, localtime
from flags import BotFeature
from mongodb.factory import TimerManager, BotFeatureUsageDataManager, MessageRecordStatisticsManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageEventText


def process_timer_get(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    tmrs = TimerManager.get_timers(e.channel_oid, e.content)

    if tmrs.has_data:
        BotFeatureUsageDataManager.record_usage_async(BotFeature.TXT_TMR_GET, e.channel_oid, e.user_model.id)

        return [HandledMessageEventText(content=tmrs.to_string(e.user_model))]

    return []


def process_timer_notification(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    within_secs = min(
        TimerManager.get_notify_within_secs(
            MessageRecordStatisticsManager.get_message_frequency(e.channel_oid, Bot.Timer.MessageFrequencyRangeMin)
        ),
        Bot.Timer.MaxNotifyRangeSeconds
    )

    crs = list(TimerManager.get_notify(e.channel_oid, within_secs))
    crs2 = list(TimerManager.get_time_up(e.channel_oid))

    ret = []

    if crs2:
        ret.append(_("**{} timer(s) have timed up!**").format(len(crs2)))
        ret.append("")

        for tmr in crs2:
            ret.append(_("- {event} has timed up! (at {time})").format(
                event=tmr.title, time=localtime(tmr.target_time, e.user_model.config.tzinfo)
            ))

    if crs:
        if ret:
            ret.append("-------------")

        now = now_utc_aware()
        ret.append(_("**{} timer(s) will time up in less than {:.0f} minutes!**").format(len(crs), within_secs / 60))
        ret.append("")

        for tmr in crs:
            ret.append(_("- {event} will time up after [{diff}]! (at {time})").format(
                event=tmr.title, diff=t_delta_str(tmr.get_target_time_diff(now)),
                time=localtime(tmr.target_time, e.user_model.config.tzinfo)
            ))

    if ret and ret[-1] == "":
        ret = ret[:-1]

    if ret:
        return [HandledMessageEventText(content="\n".join(ret))]
    else:
        return []
