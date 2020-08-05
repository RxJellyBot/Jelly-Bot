from django.utils.translation import activate, deactivate

from mongodb.factory import MessageRecordStatisticsManager, ProfileManager

from .models.pipe_in import (
    MessageEventObject, TextMessageEventObject, ImageMessageEventObject, LineStickerMessageEventObject
)
from .models.pipe_out import HandledMessageEventsHolder
from .logger import logger

__all__ = ["load_handling_functions", "unload_handling_functions",
           "handle_message_main", "HandlingFunctionsNotLoadedError"]

# Creating this because some imports cannot be import before the django framework has been fully loaded
_fn_box = {}


class HandlingFunctionsNotLoadedError(Exception):
    def __init__(self):
        super().__init__("Handling functions not yet loaded.")


def load_handling_functions():
    global _fn_box

    from .text.main import handle_text_event
    from .img.main import handle_image_event
    from .stk.main import handle_line_sticker_event

    _fn_box = {
        TextMessageEventObject: handle_text_event,
        ImageMessageEventObject: handle_image_event,
        LineStickerMessageEventObject: handle_line_sticker_event
    }


def unload_handling_functions():
    global _fn_box

    _fn_box = {}


def handle_message_main(e: MessageEventObject) -> HandledMessageEventsHolder:
    if not _fn_box:
        raise HandlingFunctionsNotLoadedError()

    has_user_model = hasattr(e, "user_model") and e.user_model is not None

    # Record message for stats / User model could be `None` on LINE
    MessageRecordStatisticsManager.record_message_async(
        e.channel_model.id, e.user_model.id if has_user_model else None,
        e.message_type, e.content, e.constructed_time)

    try:
        if has_user_model:
            # Ensure User existence in channel
            ProfileManager.register_new_default_async(e.channel_model.id, e.user_model.id)

            # Translation activation
            activate(e.user_model.config.language)
        else:
            # User model could be `None` if user token is not provided. This happens on LINE.
            # Notify users when they attempted to use any features related of the Jelly Bot
            from .spec.no_utoken import handle_no_user_token

            return HandledMessageEventsHolder(e.channel_model, handle_no_user_token(e))

        # Main handle process
        event_type = type(e)
        if event_type in _fn_box:
            ret = HandledMessageEventsHolder(e.channel_model, _fn_box[event_type](e))
        else:
            logger.logger.info(f"Message handle object not handled. Raw: {e.raw}")
            ret = HandledMessageEventsHolder(e.channel_model)

        # Translation deactivation
        deactivate()

        return ret
    except Exception as ex:
        from .spec.error import handle_error_main

        return HandledMessageEventsHolder(e.channel_model, handle_error_main(e, ex))
