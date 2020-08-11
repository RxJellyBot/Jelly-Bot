from typing import List

from msghandle.models import ImageMessageEventObject, HandledMessageEvent, HandledMessageEventText
from strres.msghandle import HandledResult
from .imgur import process_imgur_upload


def handle_image_event(e: ImageMessageEventObject) -> List[HandledMessageEvent]:
    if e.is_test_event:
        return [HandledMessageEventText(content=HandledResult.TestSuccessImage)]

    handle_fn = [
        process_imgur_upload
    ]

    for fn in handle_fn:
        responses = fn(e)
        if responses:
            return responses

    return []
