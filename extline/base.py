import os
import sys

from linebot import WebhookParser
from linebot.models import MessageEvent

from .handler import handle_main, handle_msg_main

__all__ = ["line_handle_event", "line_parser"]


line_secret = os.environ.get("LINE_SECRET")
if not line_secret:
    print("Specify Line webhook secret as LINE_SECRET in environment variables.")
    sys.exit(1)

line_parser = WebhookParser(line_secret)


# TODO: Longtime message: No lock - set timeout (Needs multithread)

def line_handle_event(request, body, signature):
    payload = line_parser.parse(body, signature, as_payload=True)

    for event in payload.events:
        if isinstance(event, MessageEvent):
            handle_msg_main(request, event, payload.destination)
        else:
            handle_main(request, event, payload.destination)
