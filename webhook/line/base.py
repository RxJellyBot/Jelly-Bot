import os
import sys
from multiprocessing.pool import ThreadPool

from linebot import LineBotApi, WebhookHandler

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

line_handle_pool = ThreadPool(processes=6)


def line_handle_event(body, signature):
    line_handle_pool.apply_async(line_handler.handle, args=(body, signature))
