"""
Main entry point for message handling regardless the platform.

The actual message handling entry point will differ:

- LINE starts from :class:`extline.handler.main.handle_main()`

- Discord starts from :class:`extdiscord.handle.handle_discord_main()`
"""
from typing import Type

from django.utils.translation import activate, deactivate

from mongodb.factory import MessageRecordStatisticsManager, ProfileManager

from .models.pipe_in import (
    MessageEventObject, TextMessageEventObject, ImageMessageEventObject, LineStickerMessageEventObject
)
from .models.pipe_out import HandledMessageEventsHolder
from .logger import logger

__all__ = ("HandlingFunctionBox", "handle_message_main", "HandlingFunctionsNotLoadedError")


# Lazy loading handling functions because some imports requires Django to be fully loaded first
class HandlingFunctionBox:
    """A class to manage the message handling functions."""

    _functions = {}

    @classmethod
    def load(cls):
        """Load the handling functions."""
        # Inline import to prevent the thing that this class wants to avoid

        # pylint: disable=import-outside-toplevel

        from .text.main import handle_text_event
        from .img.main import handle_image_event
        from .stk.main import handle_line_sticker_event

        # pylint: enable=import-outside-toplevel

        cls._functions = {
            TextMessageEventObject: handle_text_event,
            ImageMessageEventObject: handle_image_event,
            LineStickerMessageEventObject: handle_line_sticker_event
        }

    @classmethod
    def unload(cls):
        """Unload the handling functions."""
        cls._functions = {}

    @classmethod
    def check_loaded(cls):
        """
        Check if the handling functions are loaded. If not, raises :class:`HandlingFunctionsNotLoadedError`.

        :raises HandlingFunctionsNotLoadedError: if the handling functions are not loaded but this method was called
        """
        if not cls._functions:
            raise HandlingFunctionsNotLoadedError()

    @classmethod
    def get_handling_function(cls, event_type: Type[MessageEventObject]) -> callable:
        """
        Get the handling function for the message event type ``event_type``.

        :param event_type: type of the message event
        :return: handling function for the message event type
        :raises NoCorrespondingHandlingFunctionError: if no corresponding message handling function was found
        """
        ret = cls._functions.get(event_type)

        if not ret:
            raise NoCorrespondingHandlingFunctionError(event_type)

        return ret


class HandlingFunctionsNotLoadedError(Exception):
    """Raised if handling functions are not yet loaded but ``handle_message_main()`` was called."""

    def __init__(self):
        super().__init__("Handling functions not yet loaded.")


class NoCorrespondingHandlingFunctionError(ValueError):
    """Raised if no corresponding handling function for the message type."""

    def __init__(self, event_type: Type[MessageEventObject]):
        super().__init__(f"No corresponding message handling function of type {type(event_type)}")


def handle_message_main(e: MessageEventObject) -> HandledMessageEventsHolder:
    """
    Main message handling function.

    This method handles the message first, then record the message after handling it.

    To call this method, ``HandlingFunctionBox.load()`` needs to be called first. The reason of this mechanism is to
    avoid translation not prepared error.

    :param e: event object to be handled
    :return: handled messages
    :raises HandlingFunctionsNotLoadedError: if this method was called but the handling functions are not loaded yet
    """
    HandlingFunctionBox.check_loaded()

    has_user_model = hasattr(e, "user_model") and e.user_model is not None

    ret = _handle_message(e, has_user_model)

    # Record message for stats / User model could be `None` on LINE
    MessageRecordStatisticsManager.record_message_async(
        e.channel_model.id, e.user_model.id if has_user_model else None,
        e.message_type, e.content, e.constructed_time)

    return ret


def _handle_message(e: MessageEventObject, has_user_model: bool) -> HandledMessageEventsHolder:
    try:
        if has_user_model:
            # Ensure User existence in channel
            ProfileManager.register_new_default_async(e.channel_model.id, e.user_model.id)

            # Translation activation
            activate(e.user_model.config.language)
        else:
            # User model could be `None` if user token is not provided. This happens on LINE.
            # Notify users when they attempted to use any features related of the Jelly Bot
            from .spec.no_utoken import handle_no_user_token  # pylint: disable=import-outside-toplevel

            return HandledMessageEventsHolder(e.channel_model, handle_no_user_token(e))

        # Main handle process
        ret = HandledMessageEventsHolder(e.channel_model, HandlingFunctionBox.get_handling_function(type(e))(e))
    except NoCorrespondingHandlingFunctionError:
        logger.logger.warning("Message handle object not handled. Raw: %s", e.raw)

        ret = HandledMessageEventsHolder(e.channel_model)
    except Exception as ex:
        from .spec.error import handle_error_main  # pylint: disable=import-outside-toplevel

        ret = HandledMessageEventsHolder(e.channel_model, handle_error_main(e, ex))

    deactivate()

    return ret
