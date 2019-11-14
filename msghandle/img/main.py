from typing import List

from msghandle.models import ImageMessageEventObject, HandledMessageEvent

from .imgur import process_imgur_upload


def handle_image_event(e: ImageMessageEventObject) -> List[HandledMessageEvent]:
    handle_fn = [
        process_imgur_upload
    ]

    for fn in handle_fn:
        responses = fn(e)
        if responses:
            return responses

    return []
