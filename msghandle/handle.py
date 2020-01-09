from django.utils.translation import activate, deactivate

from mongodb.factory import MessageRecordStatisticsManager, ProfileManager

from .models.pipe_in import (
    MessageEventObject, TextMessageEventObject, ImageMessageEventObject, LineStickerMessageEventObject
)
from .models.pipe_out import HandledMessageEventsHolder
from .logger import logger


# Creating this because some imports cannot be import before the django framework has been fully loaded
fn_box = {}


def load_handling_functions():
    from .text.main import handle_text_event
    from .img.main import handle_image_event
    from .stk.main import handle_line_sticker_event

    fn_box[TextMessageEventObject] = handle_text_event
    fn_box[ImageMessageEventObject] = handle_image_event
    fn_box[LineStickerMessageEventObject] = handle_line_sticker_event


def handle_message_main(e: MessageEventObject) -> HandledMessageEventsHolder:
    try:
        if e.user_model:
            # Ensure User existence in channel
            ProfileManager.register_new_default_async(e.channel_model.id, e.user_model.id)

            # Translation activation
            activate(e.user_model.config.language)
        else:
            # User model could be `None` if user token is not provided. This happens on LINE.
            # Notify users when they attempted to use any features related of the Jelly Bot
            from .spec.no_utoken import handle_no_user_token

            return HandledMessageEventsHolder(handle_no_user_token(e))

        # Main handle process
        event_type = type(e)
        if event_type in fn_box:
            ret = HandledMessageEventsHolder(fn_box[event_type](e))
        else:
            logger.logger.info(f"Message handle object not handled. Raw: {e.raw}")
            ret = HandledMessageEventsHolder()

        # Translation deactivation
        deactivate()

        # Record message for stats / User model could be `None` on LINE
        if e.user_model:
            MessageRecordStatisticsManager.record_message_async(
                e.channel_model.id, e.user_model.id, e.message_type, e.content, e.constructed_time)

        return ret
    except Exception as ex:
        from .spec.error import handle_error_main

        return HandledMessageEventsHolder(handle_error_main(e, ex))
