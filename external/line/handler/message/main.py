from linebot.models import (
    TextMessage
)
from flags import MessageType

from ..error import handle_error
from .text import handle_text
from .default import handle_msg_default


fn_dict = {
    MessageType.UNKNOWN: handle_msg_default,
    MessageType.TEXT: handle_text
}


def handle_msg_main(event, destination):
    # FIXME: List all types of message events and handle
    print(f"[LINE] Event: {event} | To: {destination}")

    if isinstance(event.message, TextMessage):
        msg_type = MessageType.TEXT
    else:
        msg_type = MessageType.UNKNOWN

    fn = fn_dict.get(msg_type)

    if fn:
        try:
            fn(event, destination)
        except Exception as e:
            handle_error(e, event, destination)
    else:
        raise ValueError("[LINE] Message type not handled.")
