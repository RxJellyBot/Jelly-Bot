import os
import sys

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


# FIXME: [HP] May need Celery with Django for async requests (solve MongoDB fork error
#   https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
#   Type "SSS" for 5 s delay, test = SSS (in 5sec) ERRORTEST and check output

def line_handle_event(body, signature):
    line_handler.handle(body, signature)
