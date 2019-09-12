from webhook.line import LineApiWrapper
from linebot.models import MessageEvent, TextMessage

from ..base import line_handler


@line_handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    # FIXME: Implement total handle and return all at once somewhere

    LineApiWrapper.reply_text(event.reply_token, event.message.text)
