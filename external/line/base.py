import asyncio
import os
import sys
from multiprocessing import Pool, cpu_count

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent
from external.line import handler

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
# Attach events
line_handler.add(MessageEvent)(handler.handle_msg_main)
line_handler.default()(handler.handle_main)

line_handle_pool = Pool(processes=cpu_count())


def line_handle_event(body, signature):
    async def handle():
        line_handler.handle(body, signature)
    asyncio.run(handle())
