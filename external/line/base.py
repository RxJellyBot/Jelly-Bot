import asyncio
import os
import sys
from multiprocessing import Pool, cpu_count

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

line_handle_pool = Pool(processes=cpu_count())


def line_handle_event(body, signature):
    async def handle():
        # TEMP:
        print("HANDLE")
        line_handler.handle(body, signature)
    print("FN CREATED")
    asyncio.run(handle())


from external.line import LineApiWrapper
from linebot.models import MessageEvent, TextMessage


@line_handler.add(MessageEvent, message=TextMessage)
def handle_text(event, dest):
    print(f"Line event triggered. [TextMessage]: {dest}")
    # FIXME: [HP] Implement total handle and return all at once somewhere
    # FIXME: Add webhook/bot links on home page
    # FIXME: [MP] https://discordpy.readthedocs.io/en/latest/logging.html / LOGGER = logging.getLogger('linebot')
    # FIXME: Discord handler

    LineApiWrapper.reply_text(event.reply_token, event.message.text)
