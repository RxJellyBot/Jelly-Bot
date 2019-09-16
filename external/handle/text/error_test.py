from typing import List

from external.handle import TextEventObject, HandledEventObject


def process_error_test(e: TextEventObject) -> List[HandledEventObject]:
    if e.text == "ERRORTEST":
        raise Exception("Custom error for testing purpose.")
    else:
        return []
