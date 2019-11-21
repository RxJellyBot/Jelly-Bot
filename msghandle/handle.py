from django.utils.translation import activate, deactivate

from mongodb.factory import MessageRecordStatisticsManager, ProfileManager

from .models.pipe_in import (
    MessageEventObject, TextMessageEventObject, ImageMessageEventObject, LineStickerMessageEventObject
)
from .models.pipe_out import HandledMessageEventsHolder


def handle_message_main(e: MessageEventObject) -> HandledMessageEventsHolder:
    if e.user_model:
        # Ensure User existence in channel
        ProfileManager.register_new_default_async(e.channel_model.id, e.user_model.id)

        # Translation activation
        activate(e.user_model.config.language)

    # Main handle process
    if isinstance(e, TextMessageEventObject):
        from .text.main import handle_text_event

        ret = HandledMessageEventsHolder(handle_text_event(e))
    elif isinstance(e, ImageMessageEventObject):
        from .img.main import handle_image_event

        ret = HandledMessageEventsHolder(handle_image_event(e))
    elif isinstance(e, LineStickerMessageEventObject):
        from .stk.main import handle_line_sticker_event

        ret = HandledMessageEventsHolder(handle_line_sticker_event(e))
    else:
        from .logger import logger

        logger.logger.info(f"Message handle object not handled. Raw: {e.raw}")
        ret = HandledMessageEventsHolder()

    # User model could be `None` if user token is not provided. This happens on LINE.
    # Notify users when they attempted to use any features related of the Jelly Bot
    if ret and not e.user_model:
        from .spec.no_utoken import handle_no_user_token

        return HandledMessageEventsHolder(handle_no_user_token(e))

    # Translation deactivation
    deactivate()

    # Record message for stats
    MessageRecordStatisticsManager.record_message_async(
        e.channel_model.id, e.user_model.id, e.message_type, e.content, e.constructed_time)

    return ret
