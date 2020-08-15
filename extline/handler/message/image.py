"""This module contains the function to handle the image message type event."""
from flags import Platform
from msghandle import handle_message_main
from msghandle.models import MessageEventObjectFactory


def handle_image(_, event, destination):
    """Method to be called upon receiving an image message type event."""
    bot_event = MessageEventObjectFactory.from_line(event, destination)

    handle_message_main(bot_event).to_platform(Platform.LINE).send_line(event.reply_token)
