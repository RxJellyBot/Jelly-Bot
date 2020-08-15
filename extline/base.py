"""Contains the main objects necessary for the LINE bot webhook to operate."""
import os
import sys

from linebot import WebhookParser
from linebot.models import MessageEvent

from extutils.logger import SYSTEM

from .handler import handle_main, handle_msg_main

__all__ = ("line_handle_event", "line_parser",)


line_secret = os.environ.get("LINE_SECRET")
if not line_secret:
    SYSTEM.logger.critical("Specify Line webhook secret as LINE_SECRET in environment variables.")
    sys.exit(1)

line_parser = WebhookParser(line_secret)
"""LINE's webhook parser."""


def line_handle_event(request, body, signature):
    """
    Main function to be called upon receiving a LINE webhook event.

    This function will call the corresponding event handling function.
    """
    payload = line_parser.parse(body, signature, as_payload=True)

    for event in payload.events:
        if isinstance(event, MessageEvent):
            handle_msg_main(request, event, payload.destination)
        else:
            handle_main(request, event, payload.destination)
