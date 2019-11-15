from typing import List

from msghandle.models import LineStickerMessageEventObject, HandledMessageEvent

from .info import process_display_info


def handle_line_sticker_event(e: LineStickerMessageEventObject) -> List[HandledMessageEvent]:
    handle_fn = [
        process_display_info
    ]

    for fn in handle_fn:
        responses = fn(e)
        if responses:
            return responses

    return []
