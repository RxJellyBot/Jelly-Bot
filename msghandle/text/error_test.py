from typing import List

from flags import BotFeature
from mongodb.factory import BotFeatureUsageDataManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent


def process_error_test(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    if e.text == "ERRORTEST":
        BotFeatureUsageDataManager.record_usage_async(BotFeature.TXT_FN_ERROR_TEST, e.channel_oid, e.user_model.id)
        raise Exception("Custom error for testing purpose.")
    else:
        return []
