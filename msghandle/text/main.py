from typing import List

from msghandle.models import TextMessageEventObject, HandledMessageEvent

from .autoreply import process_auto_reply
from .error_test import process_error_test
from .calculator import process_calculator
from .botcmd import process_bot_cmd


def handle_text_event(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    handle_fn = [process_error_test]

    if e.channel_model.config.enable_bot_command:
        handle_fn.append(process_bot_cmd)

    if e.channel_model.config.enable_auto_reply:
        handle_fn.append(process_auto_reply)

    if e.channel_model.config.enable_calculator:
        handle_fn.append(process_calculator)

    for fn in handle_fn:
        responses = fn(e)
        if responses:
            return responses

    return []
