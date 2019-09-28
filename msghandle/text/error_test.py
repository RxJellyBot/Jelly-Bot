from typing import List

from msghandle.models import TextMessageEventObject, HandledMessageEvent


def process_error_test(e: TextMessageEventObject) -> List[HandledMessageEvent]:
    if e.text == "ERRORTEST":
        raise Exception("Custom error for testing purpose.")
    else:
        return []
