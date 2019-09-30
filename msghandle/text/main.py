from typing import List

from msghandle.models import TextMessageEventObject, HandledMessageEvent

from .autoreply import process_auto_reply
from .error_test import process_error_test
from .calculator import process_calculator
from .botcmd import process_bot_cmd


def handle_text_event(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    handle_fn = [
        process_error_test,
        process_bot_cmd,
        process_auto_reply,
        process_calculator
    ]

    for fn in handle_fn:
        responses = fn(e)
        if responses:
            return responses

    return []
