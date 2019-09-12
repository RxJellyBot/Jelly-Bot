import asyncio
import os
import sys
from multiprocessing import Pool, cpu_count

from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent,
    TextMessage
)

from flags import MessageType

__all__ = ["line_handle_event", "line_api", "line_handler"]

line_token = os.environ.get("LINE_TOKEN")
if not line_token:
    print("Specify Line webhook access token as LINE_TOKEN in environment variables.")
    sys.exit(1)

line_secret = os.environ.get("LINE_SECRET")
if not line_secret:
    print("Specify Line webhook secret as LINE_SECRET in environment variables.")
    sys.exit(1)

line_api = LineBotApi(line_token)
line_handler = WebhookHandler(line_secret)

line_handle_pool = Pool(processes=cpu_count())


def line_handle_event(body, signature):
    async def handle():
        line_handler.handle(body, signature)
    asyncio.run(handle())


# For some reason, LINE event handler cannot be attached in different file, or the function will never being executed


@line_handler.default()
def handle_main(event, destination):
    print(f"[LINE] Event Type: {event.type} | To: {destination}")
    print(f"[LINE] Event Message Type: {event.message.type} | To: {destination}")
    print(isinstance(event.type, MessageEvent))
    print(isinstance(event.message.type, TextMessage))
    #
    # try:
    #     if msgtype == MessageType.UNKNOWN:
    #         handle_default(event, destination)
    #         return
    #     elif msgtype == MessageType.TEXT:
    #         handle_text(event, destination)
    #         return
    # except Exception as e:
    #     handle_error(e, event, destination)
    #
    # raise ValueError(f"Unhandled LINE message type ({msgtype}).")
