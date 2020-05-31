import logging

from linebot.models import (
    TextMessage, ImageMessage, VideoMessage, AudioMessage, LocationMessage, StickerMessage, FileMessage
)
from flags import MessageType
from extline import LINE, ExtraKey, event_dest_fmt

from ..error import handle_error
from .text import handle_text
from .image import handle_image
from .sticker import handle_sticker
from .default import handle_msg_default


fn_dict = {
    MessageType.UNKNOWN: handle_msg_default,
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
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Message event",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})

    fn = fn_dict.get(_get_message_type(event.message))

    try:
        if fn:
            fn(request, event, destination)
        else:
            handle_msg_default(request, event, destination)
    except Exception as e:
        handle_error(e, f"Error occurred in handle_msg_main. Handle function: {fn.__qualname__}", event, destination)
