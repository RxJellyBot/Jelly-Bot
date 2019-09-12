from external.line import LineApiWrapper
from linebot.models import MessageEvent, TextMessage

from ..base import line_handler


@line_handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    print("Line event triggered. [TextMessage]")
    # FIXME: [HP] Implement total handle and return all at once somewhere
    # FIXME: Add webhook/bot links on home page
    # FIXME: [MP] https://discordpy.readthedocs.io/en/latest/logging.html
    # FIXME: Discord handler

    LineApiWrapper.reply_text(event.reply_token, event.message.text)
