from typing import List

from django.utils.translation import gettext_lazy as _

from flags import ChannelType
from msghandle.models import LineStickerMessageEventObject, HandledMessageEvent, HandledMessageEventText


def process_display_info(e: LineStickerMessageEventObject) -> List[HandledMessageEvent]:
    if e.channel_type == ChannelType.PRIVATE_TEXT:
        sticker_info = e.content

        return [HandledMessageEventText(
            content=_("Sticker ID: `{}`\nPackage ID: `{}`").format(sticker_info.sticker_id, sticker_info.package_id),
            bypass_multiline_check=True)]
    else:
        return []
