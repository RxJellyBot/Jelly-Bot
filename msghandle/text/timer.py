from typing import List

from flags import AutoReplyContentType, BotFeature
from mongodb.factory import AutoReplyContentManager, TimerManager, BotFeatureUsageDataManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent, HandledMessageEventText


def process_timer(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    ctnt_res = AutoReplyContentManager.get_content(e.content, AutoReplyContentType.TEXT, add_on_not_found=False)
    if not ctnt_res.model:
        return []

    tmrs = TimerManager.get_timer(e.channel_oid, ctnt_res.model.id)

    if tmrs.has_data:
        BotFeatureUsageDataManager.record_usage_async(BotFeature.TXT_TMR_GET, e.channel_oid, e.user_model.id)

        return [HandledMessageEventText(content=tmrs.to_string(e.user_model))]

    return []
