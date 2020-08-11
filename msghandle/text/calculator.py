from typing import List

from flags import BotFeature
from mongodb.factory import BotFeatureUsageDataManager
from msghandle.models import TextMessageEventObject, HandledMessageEvent
from bot.utils import calculate_expression

__all__ = ["process_calculator"]


# Obtained and modified from https://stackoverflow.com/a/14822667
def process_calculator(e: TextMessageEventObject, output_error: bool = False) -> List[HandledMessageEvent]:
    if e.text and e.text[-1] == "=":
        BotFeatureUsageDataManager.record_usage_async(BotFeature.TXT_FN_CALCULATOR, e.channel_oid, e.user_model.id)

        expr = e.text[:-1]

        return calculate_expression(expr, output_error)
    else:
        return []
