import os
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count

from linebot import WebhookHandler
from linebot.models import MessageEvent

from .handler import handle_main, handle_msg_main

__all__ = ["line_handle_event", "line_handler"]


line_secret = os.environ.get("LINE_SECRET")
if not line_secret:
    print("Specify Line webhook secret as LINE_SECRET in environment variables.")
    sys.exit(1)

line_handler = WebhookHandler(line_secret)
# Attach events
line_handler.add(MessageEvent)(handle_msg_main)
line_handler.default()(handle_main)

line_handle_pool = Pool(processes=cpu_count())

with ThreadPoolExecutor(max_workers=5) as executor:
    def line_handle_event(body, signature):
        executor.submit(line_handler.handle, body, signature).result()
