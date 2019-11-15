from gettext import gettext as _
from typing import List

from flags import ChannelType
from msghandle.models import LineStickerMessageEventObject, HandledMessageEvent, HandledMessageEventText


def process_display_info(e: LineStickerMessageEventObject) -> List[HandledMessageEvent]:
    if e.channel_type == ChannelType.PRIVATE_TEXT:
        sticker_info = e.content

        return [HandledMessageEventText(
            content=_(f"Sticker ID: {sticker_info.sticker_id}"
                      f"Package ID: {sticker_info.package_id}"),
            bypass_multiline_check=True)]
    else:
        return []
