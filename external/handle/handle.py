from .base_in import EventObject, TextEventObject
from .logger import logger
from .text.main import handle_text_event


def handle_main(e: EventObject):
    if isinstance(e, TextEventObject):
        return handle_text_event(e)
    else:
        logger.logger.info(f"Message handle object not handled")