from typing import List

from external.handle import TextEventObject, HandledEventObject

from .autoreply import process_auto_reply
from .error_test import process_error_test
from .calculator import process_calculator


def handle_text_event(e: TextEventObject) -> List[HandledEventObject]:
    handle_fn = [
        process_error_test,
        process_auto_reply,
        process_calculator
    ]

    for fn in handle_fn:
        responses = fn(e)
        if responses:
            return responses
