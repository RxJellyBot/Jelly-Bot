from .base_in import EventObject, TextEventObject
from .base_out import HandledEventsHolder
from .logger import logger
from .text.main import handle_text_event


def handle_main(e: EventObject) -> HandledEventsHolder:
    if isinstance(e, TextEventObject):
        return HandledEventsHolder(handle_text_event(e))
    else:
        logger.logger.info(f"Message handle object not handled. Raw: {e.raw}")
        return HandledEventsHolder()
