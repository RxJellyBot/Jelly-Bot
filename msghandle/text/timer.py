from typing import List

from django.utils.translation import gettext_lazy as _
from django.utils.timezone import localtime

from extutils.dt import now_utc_aware, t_delta_str
from flags import AutoReplyContentType, BotFeature
from mongodb.factory import AutoReplyContentManager, TimerManager, BotFeatureUsageDataManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageEventText


def process_timer(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    ctnt_res = AutoReplyContentManager.get_content(e.content, AutoReplyContentType.TEXT, add_on_not_found=False)
    if not ctnt_res.model:
        return []

    tmrs = TimerManager.get_timer(ctnt_res.model.id)

    if tmrs.has_data:
        BotFeatureUsageDataManager.record_usage_async(BotFeature.TXT_TMR_GET, e.channel_oid, e.user_model.id)

        now = now_utc_aware()
        tzinfo = e.user_model.config.tzinfo

        ret = []

        if tmrs.future:
            for tmr in tmrs.future:
                ret.append(
                    _("[{diff}] to {event} (at {time})").format(
                        event=tmr.title, diff=t_delta_str(tmr.get_target_time_diff(now)),
                        time=localtime(tmr.target_time, tzinfo)
                    ))
            ret.append("")  # Separator

        if tmrs.past_continue:
            for tmr in tmrs.past_continue:
                ret.append(
                    _("[{diff}] past {event} (at {time})").format(
                        event=tmr.title, diff=t_delta_str(tmr.get_target_time_diff(now)),
                        time=localtime(tmr.target_time, tzinfo)
                    ))
            ret.append("")  # Separator

        if tmrs.past_done:
            for tmr in tmrs.past_done:
                ret.append(
                    _("{event} has ended (at {time})").format(
                        event=tmr.title, time=localtime(tmr.target_time, tzinfo)))

        return [HandledMessageEventText(content="\n".join(ret))]

    return []
