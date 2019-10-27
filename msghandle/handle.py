from django.utils.translation import activate, deactivate

from mongodb.factory import MessageRecordStatisticsManager

from .models.pipe_in import MessageEventObject, TextMessageEventObject
from .models.pipe_out import HandledMessageEventsHolder
from .logger import logger
from .text.main import handle_text_event
from .translation import update_current_lang, deactivate_lang


def handle_message_main(e: MessageEventObject) -> HandledMessageEventsHolder:
    # Record message for stats
    MessageRecordStatisticsManager.record_message(e.channel_model.id, e.user_model.id, e.message_type, e.content)

    # Translation activation
    update_current_lang('msghandle', e.user_model.config.language)
    activate(e.user_model.config.language)

    # Main handle process
    if isinstance(e, TextMessageEventObject):
        ret = HandledMessageEventsHolder(handle_text_event(e))
    else:
        logger.logger.info(f"Message handle object not handled. Raw: {e.raw}")
        ret = HandledMessageEventsHolder()

    # Translation deactivation
    deactivate()
    deactivate_lang()

    return ret
