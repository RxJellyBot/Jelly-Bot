"""This module contains the function to handle all types of the mesage event from the LINE bot webhook."""
from linebot.models import (
    TextMessage, ImageMessage, VideoMessage, AudioMessage, LocationMessage, StickerMessage, FileMessage
)
from flags import MessageType
from extline.logger import LINE

from ..error import handle_error
from .text import handle_text
from .image import handle_image
from .sticker import handle_sticker
from .default import handle_msg_unhandled


fn_dict = {
    MessageType.UNKNOWN: handle_msg_unhandled,
    MessageType.TEXT: handle_text,
    MessageType.IMAGE: handle_image,
    MessageType.LINE_STICKER: handle_sticker
}


def _get_message_type(event_message) -> MessageType:
    if isinstance(event_message, TextMessage):
        msg_type = MessageType.TEXT
    elif isinstance(event_message, ImageMessage):
        msg_type = MessageType.IMAGE
    elif isinstance(event_message, VideoMessage):
        msg_type = MessageType.VIDEO
    elif isinstance(event_message, AudioMessage):
        msg_type = MessageType.AUDIO
    elif isinstance(event_message, LocationMessage):
        msg_type = MessageType.LOCATION
    elif isinstance(event_message, StickerMessage):
        msg_type = MessageType.LINE_STICKER
    elif isinstance(event_message, FileMessage):
        msg_type = MessageType.FILE
    else:
        msg_type = MessageType.UNKNOWN

    return msg_type


def handle_msg_main(request, event, destination):
    """Method to be called upon receiving a message event from the LINE bot webhook."""
    LINE.log_event("Message event", event=event, dest=destination)

    handle_fn = fn_dict.get(_get_message_type(event.message))

    try:
        if handle_fn:
            handle_fn(request, event, destination)
        else:
            handle_msg_unhandled(request, event, destination)
    except Exception as ex:  # pylint: disable=broad-except
        handle_error(ex, f"Error occurred in handle_msg_main. Handle function: {handle_fn.__qualname__}",
                     event, destination)
