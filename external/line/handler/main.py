from .text import handle_text
from .default import handle_default
from .error import handle_error
from flags import MessageType


def handle_main(msgtype, event, destination):
    print(f"[LINE] Type: {msgtype} | To: {destination}")

    try:
        if msgtype == MessageType.UNKNOWN:
            handle_default(event, destination)
            return
        elif msgtype == MessageType.TEXT:
            handle_text(event, destination)
            return
    except Exception as e:
        handle_error(e, event, destination)

    raise ValueError(f"Unhandled LINE message type ({msgtype}).")
