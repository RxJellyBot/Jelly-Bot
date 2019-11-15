from typing import List

from flags import AutoReplyContentType, BotFeature
from mongodb.factory import AutoReplyManager, BotFeatureUsageDataManager
from msghandle.models import LineStickerMessageEventObject, HandledMessageEvent


def process_auto_reply(e: LineStickerMessageEventObject) -> List[HandledMessageEvent]:
    ret = []

    resps = AutoReplyManager.get_responses(
        e.content.sticker_id, AutoReplyContentType.LINE_STICKER, e.channel_oid)

    if resps:
        BotFeatureUsageDataManager.record_usage(BotFeature.TXT_AR_RESPOND, e.channel_oid, e.user_model.id)

        for response_model, bypass_ml_check in resps:
            casted = HandledMessageEvent.auto_reply_model_to_handled(response_model, bypass_ml_check)

            if casted:
                ret.append(casted)

    return ret
