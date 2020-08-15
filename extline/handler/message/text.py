"""This module contains the function to handle text message event."""
from flags import Platform
from msghandle import handle_message_main
from msghandle.models import MessageEventObjectFactory


def handle_text(_, event, destination):
    """Method to be called to handle text message event."""
    bot_event = MessageEventObjectFactory.from_line(event, destination)

    handle_message_main(bot_event).to_platform(Platform.LINE).send_line(event.reply_token)
