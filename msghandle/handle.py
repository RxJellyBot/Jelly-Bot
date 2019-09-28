from django.utils.translation import activate, deactivate

from mongodb.factory import MessageRecordStatisticsManager

from .models.pipe_in import MessageEventObject, TextMessageEventObject
from .models.pipe_out import HandledMessageEventsHolder
from .logger import logger
from .text.main import handle_text_event


def handle_message_main(e: MessageEventObject) -> HandledMessageEventsHolder:
    MessageRecordStatisticsManager.record_message(e.channel_model.id, e.user_model.id, e.message_type, e.content)
    activate(e.user_model.config.language)

    if isinstance(e, TextMessageEventObject):
        ret = HandledMessageEventsHolder(handle_text_event(e))
    else:
        logger.logger.info(f"Message handle object not handled. Raw: {e.raw}")
        ret = HandledMessageEventsHolder()

    deactivate()

    return ret
