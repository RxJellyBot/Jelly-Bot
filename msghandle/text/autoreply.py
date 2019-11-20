from typing import List

from flags import AutoReplyContentType, BotFeature
from JellyBot.systemconfig import AutoReply
from mongodb.factory import AutoReplyManager, BotFeatureUsageDataManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent


def process_auto_reply(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    ret = []

    resps = AutoReplyManager.get_responses(
        e.text, AutoReplyContentType.TEXT, e.channel_oid, case_insensitive=AutoReply.CaseInsensitive)

    if resps:
        BotFeatureUsageDataManager.record_usage(BotFeature.TXT_AR_RESPOND, e.channel_oid, e.user_model.id)

        for response_model, bypass_ml_check in resps:
            casted = HandledMessageEvent.auto_reply_model_to_handled(response_model, bypass_ml_check)

            if casted:
                ret.append(casted)

    return ret
