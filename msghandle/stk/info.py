from typing import List

from django.utils.translation import gettext_lazy as _

from flags import ChannelType, BotFeature
from msghandle.models import LineStickerMessageEventObject, HandledMessageEvent, HandledMessageEventText
from mongodb.factory import BotFeatureUsageDataManager


def process_display_info(e: LineStickerMessageEventObject) -> List[HandledMessageEvent]:
    if e.channel_type == ChannelType.PRIVATE_TEXT:
        sticker_info = e.content

        BotFeatureUsageDataManager.record_usage_async(BotFeature.STK_LINE_GET_INFO, e.channel_oid, e.user_model.id)

        return [HandledMessageEventText(
            content=_("Sticker ID: `{}`\nPackage ID: `{}`").format(sticker_info.sticker_id, sticker_info.package_id),
            bypass_multiline_check=True)]
    else:
        return []
