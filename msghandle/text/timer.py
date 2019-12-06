from typing import List

from django.utils.translation import gettext_lazy as _

from extutils.dt import now_utc_aware, t_delta_str
from flags import AutoReplyContentType, BotFeature
from mongodb.factory import AutoReplyContentManager, TimerManager, BotFeatureUsageDataManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent


def process_timer(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    ctnt_res = AutoReplyContentManager.get_content(e.content, AutoReplyContentType.TEXT, add_on_not_found=False)
    if not ctnt_res.model:
        return []

    tmrs = TimerManager.get_timer(ctnt_res.model.id)

    if tmrs:
        BotFeatureUsageDataManager.record_usage_async(BotFeature.TXT_TMR_GET, e.channel_oid, e.user_model.id)

        now = now_utc_aware()

        ret = []

        if tmrs.Future:
            for tmr in tmrs.Future:
                ret.append(_("{} to {}").format(t_delta_str(tmr.get_target_time_diff(now)), tmr.title))
            ret.append("\n")  # Separator

        if tmrs.PastContinue:
            for tmr in tmrs.PastContinue:
                ret.append(_("{} past {}").format(t_delta_str(tmr.get_target_time_diff(now)), tmr.title))
            ret.append("\n")  # Separator

        if tmrs.PastDone:
            for tmr in tmrs.PastDone:
                ret.append(_("{} has ended").format(tmr.title))

        return ret

    return []
