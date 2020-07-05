from typing import List

from msghandle.models import LineStickerMessageEventObject, HandledMessageEvent, HandledMessageEventText
from strres.msghandle import HandledResult
from .info import process_display_info
from .autoreply import process_auto_reply


def handle_line_sticker_event(e: LineStickerMessageEventObject) -> List[HandledMessageEvent]:
    if e.is_test_event:
        return [HandledMessageEventText(content=HandledResult.TestSuccessLineSticker)]

    handle_fn = [process_display_info]

    if e.channel_model.config.enable_auto_reply:
        handle_fn.append(process_auto_reply)

    for fn in handle_fn:
        responses = fn(e)
        if responses:
            return responses

    return []
