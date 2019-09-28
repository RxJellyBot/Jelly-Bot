from flags import Platform
from extline import LineApiWrapper
from msghandle import handle_message_main
from msghandle.models import MessageEventObjectFactory


def handle_text(request, event, destination):
    e = MessageEventObjectFactory.from_line(event)

    handled_events = handle_message_main(e).to_platform(Platform.LINE)

    LineApiWrapper.reply_text(event.reply_token, handled_events.to_send)
